import { Telegraf } from "telegraf";
import fetch from "node-fetch";
import cron from "node-cron";
import dotenv from "dotenv";

dotenv.config();

const botToken = process.env.TELEGRAM_BOT_TOKEN!;
const PRODUCT_HUNT_TOKEN = process.env.PRODUCT_HUNT_TOKEN!;

const bot = new Telegraf(botToken);

const fetchLeaderboard = async () => {
  const opts = {
    headers: {
      Authorization: `Bearer ${PRODUCT_HUNT_TOKEN}`,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    method: "POST",
    mode: "cors",
    body: JSON.stringify({
      query: `query { posts(last: 5, order: VOTES) {
                edges {
                  cursor
                  node {
                    id
                    name
                    tagline
                    description
                    url
                    votesCount
                    thumbnail {
                      type
                      url
                    }
                    website
                    reviewsRating
                  }
                }
              }
            }`,
    }),
  };

  const response = await fetch(
    "https://api.producthunt.com/v2/graphql", // 更新为正确的端点
    opts
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log(data, "data");

  return data;
};

bot.start((ctx) => ctx.reply("Welcome to Niche Hunt!"));

bot.command("leaderboard", async (ctx) => {
  console.log("Fetching Product Hunt leaderboard...");
  const leaderboard = await fetchLeaderboard();
  console.log("Leaderboard data:", leaderboard);

  try {
    const leaderboard = await fetchLeaderboard();
    ctx.replyWithMarkdownV2(
      `*Today's Leaderboard:*\n${JSON.stringify(leaderboard, null, 2)}`
    );
  } catch (error) {
    ctx.reply("Failed to fetch the leaderboard. Please try again later.");
  }
});

cron.schedule("0 0 * * *", async () => {
  // Runs every day at midnight
  const leaderboard = await fetchLeaderboard();
  // Assuming you have a list of subscribers' chat IDs
  const subscribers = [123456789, 987654321]; // Replace with actual chat IDs
  subscribers.forEach((chatId) => {
    bot.telegram.sendMessage(
      chatId,
      `*Today's Leaderboard:*\n${JSON.stringify(leaderboard, null, 2)}`
    );
  });
});

bot.launch().catch(console.error);
