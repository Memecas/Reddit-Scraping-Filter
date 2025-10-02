
import pandas as pd
import unittest
from core_filters import (
    filter_by_score,
    filter_url_only_content,
    filter_edited_content,
    eliminate_duplicates,
    filter_automoderator_and_bots
)

class TestCoreFilters(unittest.TestCase):

    def setUp(self):
        self.comments_data = {
            'score': [1, 5, 3, 1, 2, 4, 3, 2, 1, 1],
            'body': [
                'I believe I just cut flairs on, let me double-check.',
                'This is a test comment with more than ten words to check the word count filter. It\'s a good comment.',
                'I am a bot and this is an automated message.',
                'lolololol',
                'https://www.example.com',
                'This comment was edited and has a good score.',
                'My child is learning to walk, it\'s a big milestone for our family.',
                'Hola, como estas? Esto no es ingles.',
                '[removed]',
                '[deleted]'
            ],
            'author': [
                '1000100001', 'testuser', 'botuser', 'laugher', 'urlonly',
                'editeduser', 'parentuser', 'nonenglish', 'removed_comment', 'deleted_comment'
            ],
            'edited': [False, False, False, False, False, True, False, False, False, False],
            'id': [
                'fsiemgr', 'fsiemgr2', 'fsiemgr3', 'fsiemgr4', 'fsiemgr5',
                'fsiemgr6', 'fsiemgr7', 'fsiemgr8', 'fsiemgr9', 'fsiemgr10'
            ]
        }
        self.comments_df = pd.DataFrame(self.comments_data)

        self.submissions_data = {
            'score': [1, 10, 12, 1, 1, 20, 5, 3],
            'selftext': [
                'A place for members of r/ADHDers to chat with each other',
                'This is an image post with some text.',
                'This is a video post with some text.',
                '[removed]',
                '[deleted]',
                'Seeking advice on toddler discipline',
                'This is a normal English post.',
                'Esto es un post en español.'
            ],
            'title': [
                'r/ADHDers Lounge', 'Cool Image', 'Cool Video', 'Removed Post', 'Deleted Post',
                'Parenting Advice', 'English Text', 'Non English Text'
            ],
            'author': [
                'Notladub', 'ImagePoster', 'VideoPoster', 'RemovedUser', 'DeletedUser',
                'ParentingUser', 'EnglishUser', 'NonEnglishUser'
            ],
            'edited': [False, False, False, False, False, True, False, False],
            'id': [
                'gugovz', 'imgpost1', 'vidpost1', 'rempost1', 'delpost1',
                'parpost1', 'engpost1', 'nonengpost1'
            ],
            'is_video': [False, False, True, False, False, False, False, False],
            'url': [
                'https://www.reddit.com/r/ADHDers/comments/gugovz/radhders_lounge/',
                'https://i.redd.it/image.jpg',
                'https://v.redd.it/video.mp4',
                'https://www.reddit.com/r/ADHDers/comments/rempost1/removed_post/',
                'https://www.reddit.com/r/ADHDers/comments/delpost1/deleted_post/',
                'https://www.reddit.com/r/parenting/comments/parpost1/parenting_advice/',
                'https://www.reddit.com/r/english/comments/engpost1/english_text/',
                'https://www.reddit.com/r/nonenglish/comments/nonengpost1/non_english_text/'
            ],
            'removed_by_category': [None, None, None, 'automoderator', None, None, None, None]
        }
        self.submissions_df = pd.DataFrame(self.submissions_data)

    def test_filter_by_score(self):
        filtered_comments = filter_by_score(self.comments_df.copy(), min_score=2)
        self.assertEqual(len(filtered_comments), 6)
        self.assertTrue(all(filtered_comments['score'] >= 2))

        filtered_submissions = filter_by_score(self.submissions_df.copy(), min_score=5)
        self.assertEqual(len(filtered_submissions), 4)
        self.assertTrue(all(filtered_submissions['score'] >= 5))

    def test_filter_url_only_content(self):
        filtered_comments = filter_url_only_content(self.comments_df.copy(), text_column='body')
        self.assertEqual(len(filtered_comments), 9) # 'https://www.example.com' should be removed
        self.assertNotIn('https://www.example.com', filtered_comments['body'].tolist())

        filtered_submissions = filter_url_only_content(self.submissions_df.copy(), text_column='selftext')
        self.assertEqual(len(filtered_submissions), 8) # No submission is URL-only in selftext

    def test_filter_edited_content(self):
        filtered_comments = filter_edited_content(self.comments_df.copy())
        self.assertEqual(len(filtered_comments), 1) # Only 'editeduser' comment is edited
        self.assertEqual(filtered_comments['author'].iloc[0], 'editeduser')

        filtered_submissions = filter_edited_content(self.submissions_df.copy())
        self.assertEqual(len(filtered_submissions), 1) # Only 'ParentingUser' submission is edited
        self.assertEqual(filtered_submissions['author'].iloc[0], 'ParentingUser')

    def test_eliminate_duplicates(self):
        df_with_duplicates = pd.DataFrame({
            'id': ['a', 'b', 'a', 'c'],
            'text': ['one', 'two', 'one', 'three']
        })
        filtered_df = eliminate_duplicates(df_with_duplicates.copy(), subset_cols=['id'])
        self.assertEqual(len(filtered_df), 3)
        self.assertEqual(filtered_df['id'].tolist(), ['a', 'b', 'c'])

    def test_filter_automoderator_and_bots(self):
        filtered_comments = filter_automoderator_and_bots(self.comments_df.copy(), author_column='author')
        self.assertEqual(len(filtered_comments), 9) # 'botuser' should be removed
        self.assertNotIn('botuser', filtered_comments['author'].tolist())

        filtered_submissions = filter_automoderator_and_bots(self.submissions_df.copy(), author_column='author')
        self.assertEqual(len(filtered_submissions), 7) # 'RemovedUser' (automoderator) should be removed
        self.assertNotIn('RemovedUser', filtered_submissions['author'].tolist())

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


