def getTier(detailsOfCompany):
    dict_tieringEstimatedRevenue = {
        '$10B+': 1,
        '$1B-$10B': 2,
        '$500M-$1B': 2,
        '$250M-$500M': 3,
        '$100M-$250M': 3,
        '$50M-$100M': 4,
        '$10M-$50M': 4,
        '$1M-$10M': 5,
        '0-$1M': 5
    }

    EstimatedAnnualRevenue = detailsOfCompany['metrics']['estimatedAnnualRevenue']
    AnnualRevenue = detailsOfCompany['metrics']['annualRevenue']
    raised = detailsOfCompany['metrics']['raised']
    employees = detailsOfCompany['metrics']['employees']
    if EstimatedAnnualRevenue != None:
        tier = dict_tieringEstimatedRevenue[EstimatedAnnualRevenue]
    else:
        if AnnualRevenue != None:
            revenue = AnnualRevenue
        else:
            if raised != None:
                revenue = raised
            else:
                revenue == None

        if revenue != None:
            if revenue >= 10000000000:                  #* $10B or more
                tier = 1
            elif 500000000 <= revenue < 10000000000:  #* $500M-$1B or $1B-$10B
                tier = 2
            elif 100000000 <= revenue < 500000000:  #* $100M-$250M or $250M-$500M
                tier = 3
            elif 10000000 <= revenue < 100000000:  #* $10M-$50M or $50M-$100M
                tier = 4
            elif 0 <= revenue < 10000000:      #* $0-$1M or $1M-$10M
                tier = 5
        else:
            tier = 0

    return tier
