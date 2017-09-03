
import twitter

from ..slack.slackbot import SlackerAdapter

from ..utils.config import Config
from ..utils.data_handler import DataHandler
from ..utils.logger import Logger



class TwitterManager:

    MAX_TEXT_LENGTH = 135
    MAX_LINK_LENGTH = 80

    def __init__(self, slackbot=None):
        self.logger = Logger().get_logger()

        self.data_handler = DataHandler()

        config = Config()
        self.api = twitter.Api(consumer_key=config.open_api["twitter"]["CONSUMER_KEY"],
                  consumer_secret=config.open_api["twitter"]["CONSUMER_SECRET"],
                  access_token_key=config.open_api["twitter"]["ACCESS_TOKEN_KEY"],
                  access_token_secret=config.open_api["twitter"]["ACCESS_TOKEN_SECRET"])

        if slackbot is None:
            self.slackbot = SlackerAdapter(channel=config.channel.get('FEED', '#general'))
        else:
            self.slackbot = slackbot

    def tweet(self, text: str) -> None:
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[:self.MAX_TEXT_LENGTH - 3] + "..."
        try:
            self.api.PostUpdate(text)
        except BaseException as e:
            self.logger.error("tweet error: " + text)

    def feed_tweet(self, feed: tuple) -> None:
        tweet_title = "#kino_bot, #feed"
        title, link, _ = feed

        self.logger.info("tweet latest feed. title: " + title + " link: " + link)

        if len(link) > self.MAX_LINK_LENGTH:
            self.logger.info("Skip to tweet. Link length is too long. length: " +str(len(link)))
            return

        remain_text_length = self.MAX_TEXT_LENGTH - len(tweet_title) - len(link)

        if len(title) > remain_text_length:
            title = title[:remain_text_length - 3] + "..."

        self.tweet(f"{tweet_title}\n{title}\n{link}")

    def reddit_tweet(self, reddit: tuple) -> None:
        cache_data = self.data_handler.read_cache()
        cache_entry_links = set(cache_data.get("entry_links", []))

        subreddit, title, link = reddit
        if link in cache_entry_links:
            return

        subreddit = subreddit.replace("MachineLearning", "ml")

        tweet_title = "#kino_bot, #reddit_" + subreddit.lower()

        if len(link) > self.MAX_LINK_LENGTH:
            self.logger.info("Skip to tweet. Link length is too long. length: " +str(len(link)))
            return

        remain_text_length = self.MAX_TEXT_LENGTH - len(tweet_title) - len(link)

        if len(title) > remain_text_length:
            title = title[:remain_text_length - 3] + "..."

        self.tweet(f"{tweet_title}\n{title}\n{link}")

        cache_entry_links.add(link)
        self.data_handler.edit_cache(("feed_links", list(cache_entry_links)))
