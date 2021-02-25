import unittest
import sentiment_analysis.sentiment_dictionary as sd
import article_selection.article_selection as arts

class TestSentimentDictionary(unittest.TestCase):
    def test_wrong_input(self):
        text = "Flüchtlinge haben leider ein schlechtes Image."
        self.assertRaises(TypeError, sd.analyse_sentiment,text, [])
        self.assertRaises(TypeError, sd.analyse_sentiment,text, [2,3,4,"hallo"])
        self.assertRaises(TypeError, sd.analyse_sentiment,3, ["c"])
        self.assertRaises(TypeError, sd.analyse_sentiment,[text], ["c"])
        self.assertRaises(TypeError, sd.analyse_sentiment,True, ["c"])


class TestArticleSelection(unittest.TestCase):
    def test_wrong_input_is_topic_relevant(self):
        self.assertRaises(TypeError,arts.is_topic_relevant,"test")
        self.assertRaises(TypeError,arts.is_topic_relevant,3)
        self.assertRaises(TypeError,arts.is_topic_relevant,False)
        self.assertEqual(arts.is_topic_relevant({"test":3}),False)
        self.assertRaises(TypeError,arts.is_topic_relevant,{"true":False},3)
        self.assertRaises(TypeError,arts.is_topic_relevant,{"true":False},True)
        self.assertRaises(TypeError,arts.is_topic_relevant,{"true":False},[])
        self.assertRaises(TypeError,arts.is_topic_relevant,{"true":False},[2,3,5])
    
    def test_wrong_input(self):
        file_list = ["data/spiegel.json"]
        relevant_articles_base = "base"
        search_keywords = ["test"]
        arts.write_relevant_content_to_file(file_list, relevant_articles_base, search_keywords)

if __name__ == '__main__':
    unittest.main()