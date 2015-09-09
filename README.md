# ChannelAdvisor
A python wrapper for the channel advisor api.
I've been writing and testing the api in python2.7 but I learned python3 first, so it may very well work in python 3.

### Dependencies
- python2.7
- suds
- beautifulsoup
    
### Setup
- Rename ```your.cookie``` to ```data.cookie```
  - fill in the ??? next to pwd, devkey, and localID
- run the main() function
```python
import channelAdvisor
main()
```
- You should then be able to retrieve you account ID from channel advisor.
  - fill in data.cookie with your accountid (replace the last question marks)

### Usage
#### Get a dictionary of your skus and information
```python
from channelAdvisor import ChannelAdvisor
ca = ChannelAdvisor()
products = ca.getAllInventory()  # This could take a while depending on how many skus you have.
```
products will be a dictionary indexed by sku.

For example if you have a sku (1001), you can view details about that sku by doing
```python
products["1001"]
```
#### Update a sku with some information
```python
from channelAdvisor import ChannelAdvisor
ca = ChannelAdvisor()
products = ca.synchInventoryItem("1001", title="ipod", description="black 32gb ipod", upc="########")
```

I've written other functions which I'll try to document later if I have the motivation.
#### License
http://opensource.org/licenses/MIT
