def parse_reddit_data(data: dict):
    parsed_posts = []
    after = data.get('data', {}).get('after')
    for post in data.get('data', {}).get('children', []):
        post_data = post.get('data', {})
        parsed_posts.append({
            'title': post_data.get('title'),
            'num_comments': post_data.get('num_comments'),
            'author': post_data.get('author'),
            'subreddit': post_data.get('subreddit'),
            'score': post_data.get('score'),
            "likes": post_data.get('likes'),
        })
    
    return after, parsed_posts