from difflib import SequenceMatcher
import json
import re, string

pattern = re.compile('[^a-zA-Z0-9\ ]')

def similarRatio(strA, strB):
    return SequenceMatcher(None, strA, strB).ratio()

def processString(string):
    copyStr = string.strip().lower()
    copyStr = pattern.sub('', copyStr)
    copyStr = ' '.join(copyStr.split())
    return copyStr

class Product:
    def __init__(self,
                 productName,
                 manufacturer,
                 family,
                 model,
                 announcedDate):
        self.productName = productName
        self.manufacturer = manufacturer
        self.family = family
        self.model = model
        self.announcedDate = announcedDate
        
    def returnDict(self):
        if self.family == "NA":
            return {"product_name" : self.productName,
                    "manufacturer" : self.manufacturer,
                    "model" : self.model,
                    "announced_date": self.announcedDate}
        else:
            return {"product_name" : self.productName,
                    "manufacturer" : self.manufacturer,
                    "family" : self.family,
                    "model" : self.model,
                    "announced_date": self.announcedDate}
        

class Listing:
    def __init__(self,
                 title,
                 manufacturer,
                 currency,
                 price):
        self.title = title
        self.manufacturer = manufacturer
        self.currency = currency
        self.price = price
    def returnDict(self):
        return {"title" : self.title,
                "manufacturer" : self.manufacturer,
                "currency" : self.currency,
                "price" : self.price}
        
class Result:
    def __init__(self, productName):
        self.productName = productName
        self.listings = []
        
    def __init__(self, productName, listings):
        self.productName = productName
        self.listings = listings
        
    def addListing(self, listing):
        self.listings.append(listing)
        
    def returnDict(self):
        return {"product_name": self.productName,
                "listings" : [listing.returnDict() for listing in self.listings]}
                
def jsonToProduct(line):
    j = json.loads(line)
    prodName = manu = family = model = annouDate = "NA"
    if "product_name" in j:
        prodName = j["product_name"]
    if "manufacturer" in j:
        manu = j["manufacturer"]
    if "family" in j:
        family = j["family"]
    if "model" in j:
        model = j["model"]
    if "announced-date" in j:
        annouDate = j["announced-date"]
        
    return Product(prodName, manu, family, model, annouDate)

def jsonToListing(line):
    j = json.loads(line)
    title = manu = currency = price = "NA"
    if "title" in j:
        title = j["title"]
    if "manufacturer" in j:
        manu = j["manufacturer"]
    if "currency" in j:
        currency = j["currency"]
    if "price" in j:
        price = j["price"]

    return Listing(title, manu, currency, price)

products = []
productsFile = open("products.txt", "r")
for line in productsFile:
    newProduct = jsonToProduct(line)
    products.append(newProduct)

productsFile.close()

listings = []
listingsFile = open("listings.txt", "r")
for line in listingsFile:
    j = json.loads(line)
    listings.append(jsonToListing(line))

productToResult = {}
totalListings = 0
mappedListings = 0
for listing in listings:
    totalListings += 1
    listingManu = processString(listing.manufacturer)
    bestRatio = float("-inf")
    bestMatchProd = -1
    listingTitle = processString(listing.title)
    listingManu = processString(listing.manufacturer)
    for product in products:
        productManu = processString(product.manufacturer)
        productModel = processString(product.model)
        if productManu in listingManu and productModel in listingTitle:
            productTitle = processString(product.productName)
            similarityRatio = similarRatio(listingTitle, productTitle)
            if similarityRatio > bestRatio:
                bestRatio = similarityRatio
                bestMatchProd = product
    if bestMatchProd != -1:
        mappedListings += 1
        if bestMatchProd in productToResult:
            productToResult[bestMatchProd].addListing(listing)
        else:
            productToResult[bestMatchProd] = Result(bestMatchProd.productName, [listing])
    else:
        print "=================could not map====================="
        print json.dumps(listing.returnDict())+"\n"
        print listingTitle
        print listingManu
        if bestMatchProd != -1:
            print "=================closest product==================="
            print json.dumps(bestMatchProd.returnDict())+"\n"
listingsFile.close()
resultsFile = open("results.txt", "w")
for product in productToResult:
    resultsFile.write(json.dumps(productToResult[product].returnDict())+"\n")
resultsFile.close()

print mappedListings, totalListings
print "Mapped " + str(float(mappedListings)/totalListings) + "%"
