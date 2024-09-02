import { Telegraf } from "telegraf";
import fetch from "node-fetch";
import { config } from "dotenv";
import cron from "node-cron";

config();

const productHuntClientId = process.env.PRODUCT_HUNT_CLIENT_ID!;
const productHuntClientSecret = process.env.PRODUCT_HUNT_CLIENT_SECRET!;

class Product {
  id: string;
  name: string;
  tagline: string;
  description: string;
  votesCount: number;
  createdAt: string;
  featuredAt: string | null;
  website: string;
  url: string;
  ogImageUrl: string;

  constructor(data: any) {
    this.id = data.id;
    this.name = data.name;
    this.tagline = data.tagline;
    this.description = data.description;
    this.votesCount = data.votesCount;
    this.createdAt = this.convertToBeijingTime(data.createdAt);
    this.featuredAt = data.featuredAt ? "是" : "否";
    this.website = data.website;
    this.url = data.url;
    this.ogImageUrl = "";
  }

  private convertToBeijingTime(utcTimeStr: string): string {
    const utcTime = new Date(utcTimeStr);
    const offset = 8 * 60; // Beijing is UTC+8
    const beijingTime = new Date(utcTime.getTime() + offset * 60 * 1000);
    return beijingTime.toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" });
  }

  public async fetchOgImageUrl(): Promise<void> {
    try {
      const response = await fetch(this.url);
      const text = await response.text();
      const ogImageMatch = text.match(
        /<meta property="og:image" content="(.*?)"/
      );
      this.ogImageUrl = ogImageMatch ? ogImageMatch[1] : "";
    } catch (error) {
      console.error(`Failed to fetch OG image for ${this.name}: ${error}`);
    }
  }
}

async function getProductHuntToken(): Promise<string> {
  const url = "https://api.producthunt.com/v2/oauth/token";
  const payload = {
    client_id: productHuntClientId,
    client_secret: productHuntClientSecret,
    grant_type: "client_credentials",
  };

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(
      `Failed to obtain access token: ${
        response.status
      } ${await response.text()}`
    );
  }

  const data = await response.json();
  return data.access_token;
}

async function fetchProductHuntData(): Promise<Product[]> {
  const token = await getProductHuntToken();
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
  const dateStr = yesterday.toISOString().split("T")[0];
  const url = "https://api.producthunt.com/v2/api/graphql";

  const query = `
    query {
        posts(order: VOTES, postedAfter: "${dateStr}T00:00:00Z", postedBefore: "${dateStr}T23:59:59Z", after: "") {
            nodes {
                id
                name
                tagline
                description
                votesCount
                createdAt
                featuredAt
                website
                url
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(
      `Failed to fetch data from Product Hunt: ${
        response.status
      } ${await response.text()}`
    );
  }

  const data = await response.json();
  const posts = data.data.posts.nodes;
  return posts.map((post: any) => new Product(post));
}

const botToken = process.env.TELEGRAM_BOT_TOKEN!;
const bot = new Telegraf(botToken);
bot.start((ctx) => ctx.reply("Welcome to Niche Hunt!"));

bot.command("leaderboard", async (ctx) => {
  try {
    const products = await fetchProductHuntData();
    for (const product of products) {
      await product.fetchOgImageUrl();
      const message = generateProductMessage(product);
      await bot.telegram.sendMessage("1789629178", message, {
        parse_mode: "Markdown",
      });
    }
  } catch (error) {
    ctx.reply("Failed to fetch the leaderboard. Please try again later.");
  }
});

// Your main function to fetch products and send to Telegram
async function main() {
  try {
    const products = await fetchProductHuntData();
    console.log("Fetched products:", products);
    for (const product of products) {
      await product.fetchOgImageUrl();
      const message = generateProductMessage(product);
      await bot.telegram.sendMessage("1789629178", message, {
        parse_mode: "Markdown",
      });
    }
  } catch (error) {
    console.error("Error in main function:", error);
  }
}

// Function to generate the message text for each product
function generateProductMessage(product: Product): string {
  return `
        *Product Name*: *${product.name}* -> [Link](${product.website})

*TagLine*: ${product.tagline}

*Description*: ${product.description}

*Votes*: ${product.votesCount} 

*createdAt*:  ${product.createdAt}
        `;
}

// Schedule the task to run every day at midnight (Beijing time)
cron.schedule("0 0 * * *", main, {
  timezone: "Asia/Shanghai",
});

main();
