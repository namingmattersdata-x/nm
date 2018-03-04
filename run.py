from common_law.cleaners.company_name import CompanyName

print(CompanyName('yes llc').pre_process().as_dict())