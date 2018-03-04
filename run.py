from common_law.cleaners.company_name import CompanyName
from common_law.collect.collector import Collector

from pprint import PrettyPrinter
PrettyPrinter().pprint(Collector().collect(sources = "all",term = "resolute").consolidate().as_dict())