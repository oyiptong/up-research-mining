import operator
from upstudy.data.labels import LABELS, NAMESPACES, TYPES

IGNORED_INTERESTS = set(["__news_counter", "__news_home_counter"])

class Ranker(object):

    def __init__(self, uuid):
        self.uuid = uuid
        self.data = None
        self.ranker_type = None
        self.load_tree()

    def load_tree(self):
        """
        load from database if there exists ranking for that uuid and accumulate
        """
        if not self.data:
            self.data = self._generate_score_tree()

    def save():
        """
        persist ranking
        """
        pass

    def _generate_score_tree(self):
        data = {}
        for type in TYPES:
            data[type] = {}
            for ns in NAMESPACES:
                data[type][ns] = {}
                labels = LABELS.get(ns, LABELS["edrules"])
                for label in labels:
                    data[type][ns][label] = 0
        return data

    def get_rankings(self):
        """
        generate ranking for each namespace/type
        """
        rankings = {}
        for type in TYPES:
            rankings[type] = {}
            for ns in NAMESPACES:
                rankings[type][ns] = sorted(self.data[type][ns].iteritems(), key=operator.itemgetter(1), reverse=True)
        return rankings

class DayCount(Ranker):

    def __init__(self, uuid):
        super(DayCount, self).__init__(uuid)
        self.ranker_type = "daycount"

    def consume(self, data):
        for day_num, interests in data.iteritems():
            for type, ns_data in data[day_num].iteritems():
                for namespace, interest_data in data[day_num][type].iteritems():
                    for interest, counts in data[day_num][type][namespace].iteritems():
                        if interest not in IGNORED_INTERESTS:
                            if counts:
                                self.data[type][namespace][interest] += 1

class VisitCount(Ranker):

    def __init__(self, uuid):
        super(VisitCount, self).__init__(uuid)
        self.ranker_type = "visitcount"

    def consume(self, data):
        for day_num, interests in data.iteritems():
            for type, ns_data in data[day_num].iteritems():
                for namespace, interest_data in data[day_num][type].iteritems():
                    for interest, counts in data[day_num][type][namespace].iteritems():
                        if interest not in IGNORED_INTERESTS:
                            self.data[type][namespace][interest] += sum(counts)
