const Stripe = require("stripe");

let stripe;
function getStripe() {
  if (!stripe) {
    const key = process.env.STRIPE_SECRET_KEY;
    if (!key) throw new Error("STRIPE_SECRET_KEY not set in environment");
    stripe = Stripe(key);
  }
  return stripe;
}

function getTelegramApi() {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  if (!token) throw new Error("TELEGRAM_BOT_TOKEN not set");
  return `https://api.telegram.org/bot${token}`;
}

const CHANNEL_ID = process.env.CHANNEL_ID;

async function sendTelegram(chatId, text) {
  const res = await fetch(`${getTelegramApi()}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: Number(chatId),
      text,
      parse_mode: "HTML",
      disable_web_page_preview: false,
    }),
  });
  if (!res.ok) {
    const err = await res.text();
    console.error("sendMessage error:", err);
  }
}

async function createInviteLink() {
  if (!CHANNEL_ID) return null;
  const res = await fetch(`${getTelegramApi()}/createChatInviteLink`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: CHANNEL_ID,
      member_limit: 1,
    }),
  });
  if (!res.ok) {
    const err = await res.text();
    console.error("createChatInviteLink error:", err);
    return null;
  }
  const data = await res.json();
  return data.result?.invite_link || null;
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  const sig = event.headers["stripe-signature"];
  let stripeEvent;
  try {
    stripeEvent = getStripe().webhooks.constructEvent(
      event.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error("Webhook signature verification failed:", err.message);
    return { statusCode: 400, body: `Webhook Error: ${err.message}` };
  }

  if (stripeEvent.type === "checkout.session.completed") {
    const session = stripeEvent.data.object;
    const telegramId = session.metadata?.telegram_id;
    const firstName = session.metadata?.first_name || "";

    if (!telegramId) {
      console.error("No telegram_id in session metadata");
      return { statusCode: 200, body: "ok" };
    }

    console.log(`Payment completed for telegram_id: ${telegramId}`);

    const inviteLink = await createInviteLink();

    let message = `<b>✅ Оплата получена! Спасибо, ${firstName}!</b>\n\n`;
    message += `📚 <a href="${process.env.COURSE_URL || "https://jamesdor.github.io/eesti-keele-kursus/"}">Ссылка на курс</a>\n`;
    if (inviteLink) {
      message += `\n🔗 <b>Ссылка для входа в канал (одноразовая):</b>\n${inviteLink}\n`;
    }
    message += `\nЕсли возникнут вопросы — пишите.`;

    await sendTelegram(telegramId, message);

    if (process.env.ADMIN_ID) {
      const adminMsg = `<b>💰 Новая продажа!</b>\nПользователь: ${firstName}\nID: ${telegramId}`;
      await sendTelegram(process.env.ADMIN_ID, adminMsg);
    }
  }

  return { statusCode: 200, body: "ok" };
};
