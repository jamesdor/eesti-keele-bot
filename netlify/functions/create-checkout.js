const Stripe = require("stripe");

const stripe = Stripe(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event) => {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
  };

  if (event.httpMethod === "OPTIONS") return { statusCode: 200, headers, body: "" };
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, headers, body: "Method Not Allowed" };
  }

  try {
    const { telegram_id, first_name } = JSON.parse(event.body);
    if (!telegram_id) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: "telegram_id required" }) };
    }

    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items: [
        {
          price_data: {
            currency: "eur",
            product_data: {
              name: "Eesti keele kursus A1-C1",
              description: "Полный доступ к курсу эстонского языка. Грамматика, лексика, аудио, тесты, экзамены. Закрытый Telegram-канал.",
            },
            unit_amount: 1500, // 15.00 EUR
          },
          quantity: 1,
        },
      ],
      metadata: {
        telegram_id: String(telegram_id),
        first_name: first_name || "",
      },
      success_url: `https://t.me/EESTIKEELBOT_bot?start=paid_${telegram_id}`,
      cancel_url: `https://t.me/EESTIKEELBOT_bot?start=cancel`,
    });

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ url: session.url }),
    };
  } catch (err) {
    console.error("create-checkout error:", err);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
