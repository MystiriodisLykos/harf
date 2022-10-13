A package of utilities for parsing, analyzing, and displaying data in `har` files.
Particularly in relation to helping develop [locust](https://locust.io/) performance test scripts.

***HarF* is heavily biased towards REST(ish) json based apis**

Currently the project only provides a CLI and library to help track data through a har file.
The CLI (`correlations`) displays what data is used where in a har file, some basic filters, and two ways to interact with the data.
For example, if you use the `tests/example1.har` file you get the following output.
```
Value ('products') used in:  
   "entry_0.request.url[0]"  
  
Value (1) used in:  
   "entry_0.response.body[0].id",  
   "entry_1.request.url[1]",  
   "entry_1.response.body[0].id",  
   "entry_2.request.body.productId"  
  
Value ('test') used in:  
   "entry_0.response.body[0].name",  
   "entry_1.response.body[0].name"  
  
Value ('product') used in:  
   "entry_1.request.url[0]"  
  
Value (1.1) used in:  
   "entry_1.response.body[0].price"  
  
Value ('cart') used in:  
   "entry_2.request.url[0]"
```
For small `har` files this basic view is probably sufficient.
However, once you start getting into larger files with hundreds of requests and dozens of values that need to be tracked this text output is a lot to go through.
With `-i` you will be dropped into a python shell with the har data and correlation info to inspect and manipulate the data as needed.
And because I am an [obsidian](https://obsidian.md/) nerd `-o <vault_path>` will output a bunch of markdown files to the `vault_path` where every request, response, and used value gets their own file and are back-linked through usage.

![Example Obsidian graph of linked HAR data](https://github.com/MystiriodisLykos/harf/blob/dev/assets/obsidian_example.png?raw=true)
