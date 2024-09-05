import Product from './product';
async function getProductHuntToken(env) {
	const url = 'https://api.producthunt.com/v2/oauth/token';
	const payload = {
		client_id: env.PRODUCT_HUNT_CLIENT_ID,
		client_secret: env.PRODUCT_HUNT_CLIENT_SECRET,
		grant_type: 'client_credentials',
	};

	const response = await fetch(url, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload),
	});

	if (!response.ok) {
		throw new Error(`Failed to obtain access token: ${response.status} ${await response.text()}`);
	}

	const data = await response.json();
	return data.access_token;
}

async function fetchProductHuntData(env) {
	console.log('Fetching data from Product Hunt...');

	const token = await getProductHuntToken(env);
	const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
	const dateStr = yesterday.toISOString().split('T')[0];
	const url = 'https://api.producthunt.com/v2/api/graphql';

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
				  slug
				  topics {
					nodes {
					  id
					  name
					  description
					  slug
					  url
					}
				  }
			  }
			  pageInfo {
				  hasNextPage
				  endCursor
			  }
		  }
	  }`;

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${token}`,
			Accept: 'application/json',
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ query }),
	});

	if (!response.ok) {
		throw new Error(`Failed to fetch data from Product Hunt: ${response.status} ${await response.text()}`);
	}

	const data = await response.json();
	console.log('Fetched data from Product Hunt:', data.data.posts.nodes);

	const posts = data.data.posts.nodes;
	return posts.map((post) => new Product(post));
}

function generateProductHTML(product) {
	return `
  <b> ${product.topics} </b>

  <b>${product.name}</b> --- <i>${product.tagline}</i>  <a href="${product.website}">Link</a>

  <b>Product description: </b> ${product.description}

  <b>票数:</b> 🔺${product.votesCount} || <b>发布时间:</b> ${product.createdAt}
  `;
}
export { getProductHuntToken, fetchProductHuntData, generateProductHTML };
