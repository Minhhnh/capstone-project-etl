"""
This component generates a set of initial prompts that will be used to retrieve images from the LAION-5B dataset.
"""
import itertools
import logging

import dask.dataframe as dd
import dask.array as da
import pandas as pd
from tqdm import tqdm


interior_styles = [
    "art deco",
    "bauhaus",
    "bouclé",
    "maximalist",
    "brutalist",
    "coastal",
    "minimalist",
    "rustic",
    "hollywood regency",
    "midcentury modern",
    "modern organic",
    "contemporary",
    "modern",
    "scandinavian",
    "eclectic",
    "bohemiam",
    "industrial",
    "traditional",
    "transitional",
    "farmhouse",
    "country",
    "asian",
    "mediterranean",
    "rustic",
    "southwestern",
    "coastal",
    "tropical",
    "neoclassic",
    "vintage",
]

interior_prefix = [
    "comfortable",
    "luxurious",
    "simple",
]

rooms = [
    "bathroom",
    "living room",
    "hotel room",
    "lobby",
    "entrance hall",
    "kitchen",
    "family room",
    "master bedroom",
    "bedroom",
    "kids bedroom",
    "laundry room",
    "guest room",
    "home office",
    "library room",
    "playroom",
    "home theater room",
    "gym room",
    "basement room",
    "garage",
    "walk-in closet",
    "pantry",
    "gaming room",
    "attic",
    "sunroom",
    "storage room",
    "study room",
    "dining room",
    "loft",
    "studio room",
    "apartment",
]


def make_interior_prompt(room: str, prefix: str, style: str) -> str:
    """Generate a prompt for the interior design model.

    Args:
        room: room name
        prefix: prefix for the room
        style: interior style

    Returns:
        prompt for the interior design model
    """
    return f"{prefix.lower()} {room.lower()}, {style.lower()} interior design"


class GeneratePromptsComponent:
    def load() -> dd.DataFrame:
        """
        Generate a set of initial prompts that will be used to retrieve images from the LAION-5B dataset.

        Returns:
            Dask dataframe
        """
        room_tuples = itertools.product(
            rooms, interior_prefix, interior_styles)
        prompts = map(lambda x: make_interior_prompt(*x), tqdm(room_tuples))

        pandas_df = pd.DataFrame(prompts, columns=["prompts_text"])

        df = dd.from_pandas(pandas_df, npartitions=1)

        return df


if __name__ == "__main__":
    component = GeneratePromptsComponent.load()
    print(component)
