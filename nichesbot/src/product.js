export default class Product {
	id;
	name;
	tagline;
	description;
	votesCount;
	createdAt;
	featuredAt;
	website;
	url;
	ogImageUrl;
	topics; // 新增属性用于存储话题标签

	constructor(data) {
		this.id = data.id;
		this.name = data.name;
		this.tagline = data.tagline;
		this.description = data.description;
		this.votesCount = data.votesCount;
		this.createdAt = this.convertToBeijingTime(data.createdAt);
		this.featuredAt = data.featuredAt ? '是' : '否';
		this.website = data.website;
		this.url = data.url;
		this.ogImageUrl = '';
		this.topics = this.formatTopics(data.topics); // 初始化时处理话题标签
	}

	convertToBeijingTime(utcTimeStr) {
		const utcTime = new Date(utcTimeStr);
		const offset = 8 * 60; // Beijing is UTC+8
		const beijingTime = new Date(utcTime.getTime() + offset * 60 * 1000);
		return beijingTime.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
	}

	formatTopics(topicsData) {
		// 提取话题名称并格式化为 '#name1 #name2' 的形式
		return topicsData.nodes.map((node) => `#${node.name}`).join(' ');
	}

	async fetchOgImageUrl() {
		try {
			const response = await fetch(this.url);
			const text = await response.text();
			const ogImageMatch = text.match(/<meta property="og:image" content="(.*?)"/);
			this.ogImageUrl = ogImageMatch ? ogImageMatch[1] : '';
		} catch (error) {
			console.error(`Failed to fetch OG image for ${this.name}: ${error}`);
		}
	}
}
