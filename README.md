# ChannelAdvisor
A python wrapper for the channel advisor api.
I've been writing and testing the api in python2.7 but I learned python3 first, so it may very well work in python 3.

Dependencies
    suds, beautifulsoup
    
### Setup
- Create a "data.cookie" file in the directory you will be running python in
  - Inside, write "**devkey \<devkey>**" replace \<devkey> with your channeladvisor developer key
  - write "**pwd \<pwd>**"
  - write "**localID \<localID>**"
- run the main() function
```python
import channelAdvisor
main()
```
- You should then be able to retrieve you account ID from channel advisor.
  - Place this in the data.cookie file as "**accountid \<accountid>**"

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
