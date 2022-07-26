from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests, json, requests, pandas as pd, re

app = Flask(__name__)
api = Api(app)

url_comment = 'https://jsonplaceholder.typicode.com/comments'
url_post = 'https://jsonplaceholder.typicode.com/posts'

class TopComment(Resource):
    
    def get(self):
        res_comment = requests.get(url_comment)
        res_post = requests.get(url_post)
        comments = res_comment.json()
        comments_df = pd.DataFrame(comments)
        posts = res_post.json()
        posts_df = pd.DataFrame(posts)
        posts_df.columns = ['user_id', 'post_id', 'post_title', 'post_body']
        comments_df.columns = ['post_id', 'comment_id', 'user_name', 'user_email', 'comment_body']
        c_group = comments_df.groupby(['post_id'])['comment_id'].size().reset_index(name = 'comment_count')
        p_result = posts_df[['post_id', 'post_title', 'post_body']].merge(c_group, how = 'left', left_on='post_id', right_on='post_id')\
                    .sort_values(by = 'comment_count', ascending = False)
        p_result_dict = p_result.to_dict('records')
        return p_result_dict

class SearchComment(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("postId", type = int, required = False, help = 'postId: integer only')
        parser.add_argument("id", type = int, required = False, help = 'id: integer only')
        parser.add_argument("name", required = False)
        parser.add_argument("email", required = False)
        parser.add_argument("body", required = False)
        args = parser.parse_args()

        res_comment = requests.get(url_comment)
        comments = res_comment.json()
        comments_df = pd.DataFrame(comments)

        single_check = ['postId', 'id']
        contain_check = ['name', 'email', 'body']
        for dict in args:
            if (dict in single_check) & (args.get(dict) is not None):
                comments_df = comments_df.loc[(comments_df[dict] == args.get(dict))]
            if (dict in contain_check) & (args.get(dict) is not None):
                comments_df = comments_df.loc[(comments_df[dict].str.contains(args[dict], regex = False))]

        comments_df.columns = ['post_id', 'comment_id', 'user_name', 'user_email', 'comment_body']
        comment_filter_df = comments_df.to_dict('records')

        return comment_filter_df

api.add_resource(TopComment, '/topcomment/')
api.add_resource(SearchComment, '/search/')

if __name__ == "__main__":
  app.run(debug=True)
