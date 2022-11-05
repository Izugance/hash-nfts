import csv
import json
import argparse
import hashlib
from pathlib import Path


def generate_json(
    nft: dict, 
    series_total: int,
    json_dir: Path
) -> tuple[str, Path]:
    """Generate a CHIP-0007 json format for the given nft, and generate
    a file path to its json file.
    """
    json_file_path = json_dir / nft["Filename"]
    all_attributes = nft["Attributes"].split(";")
    # Gender is also an attribute.
    attributes_list = [{"trait_type": "gender", "value": nft["Gender"]}]
    for attribute in all_attributes:
        try:
            attribute, value = attribute.split(":")
        except Exception:
            # The attributes are improperly formatted.
            # Add the gender attribute to the attributes, as a string,
            # then break out of the loop.
            raw_attributes = nft["Attributes"]
            attributes_with_gender = f"gender: {nft["Gender"]} " + raw_attributes
            attributes_list = [nft["Attributes"]]
            break
        else:    
            attributes_list.append(
                {"trait_type": attribute.strip(), "value": value.strip()}
            )

    json_nft = {
        "format": "CHIP-0007",
        "name": nft["Name"],
        "description": nft["Description"],
        "miniting_tool": nft["Teams"],
        "sensitive_content": nft.get("Sensitive Content", False),
        "series_number": nft["Series Number"],
        "series_total": series_total,
        "attributes": attributes_list,
        "collection": {
            "name": "Zuri NFT Tickets for Free Lunch",
            "id": nft["UUID"],
            "attributes": [
                {
                    "type": "description",
                    "value": "Rewards for accomplishments during HNGi9.",
                }
            ],
        },
    }
    return json_nft, json_file_path


def hash_nfts(file_path: str) -> None:
    """Generate a new csv file in the current directory which
    has the same fields as the csv file referred to by `file_path`,
    but with a hash field that contains the hash for each CHIP-0007
    json format for each nft.
    """
    file_path = Path(file_path)
    tmp = Path.cwd() / "tmp"
    tmp.mkdir(exist_ok=True)
    output_file = Path.cwd() / Path(f"{file_path.stem}.output.csv")

    # Get the max Series Number. This is the series total.
    with file_path.open() as f:
        reader = csv.reader(f)
        # Skip the header.
        next(reader)
        series_total = sum(1 for row in reader)

    with output_file.open("w", newline="") as outfile:
        with file_path.open() as infile:
            nfts = csv.DictReader(infile)
            fields = ["TEAM NAMES" , "Series Number", "Filename", "Name",
                      "Description", "Gender", "Attributes", "UUID", "Hash"]

            writer = csv.DictWriter(outfile, fieldnames=fields)
            writer.writeheader()
            current_team = ""
            for nft in nfts:
                # Due to the format of the csv file, we need to update each
                # nft to have the Teams field filled.
                if nft["Teams"] and nft["Teams"] != current_team:
                    current_team = nft["Teams"]
                nft["Teams"] = current_team
                    
                json_nft, json_file_path = generate_json(nft, series_total, tmp)
                with json_file_path.open("w") as jf:
                    json.dump(json_nft, jf)
                with json_file_path.open("rb") as jf:
                    nft_hash = hashlib.sha256(jf.read()).hexdigest()
                nft["Hash"] = nft_hash
                writer.writerow(nft)
                # Get rid of the temporary json file
                json_file_path.unlink()
            # Get rid of the temporary directory.
            tmp.rmdir()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Hash the CHIP0007 JSON format "
            "of each csv line and append to "
            "a hash column."
        )
    )
    parser.add_argument("file", help="string path to the csv file", type=str)
    args = parser.parse_args()
    file_path = args.file
    hash_nfts(file_path)
