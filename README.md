# hash_nfts
This is a command line application that takes in nfts in csv form with the fields Teams, Series Number, Filename, Name, Description,
Gender, Attributes, UUID. It generates a chip-0007 json file for each nft (in a temporary directory), which is then used to
compute a hash for the nft. The output file (filename = "input_filename.output.csv") contains the same fields, but with an 
extra hash field.

To use this app:
- Clone the repo, then add the hash_nfts.py file to your current working directory, or copy the code from hash_nfts.py into a file with the
  same name into your current working directory
- From the command line, run the file as such: python hash_nfts.py "path/to/csvfile.csv"
