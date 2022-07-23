import copy

import exif
import PIL
from loguru import logger

from models import ImageDescription, TagModel
from tag import Tag


class Image:
    def __init__(self, file_name: str) -> None:
        self.__file_name = file_name
        self.__image = PIL.Image.open(file_name)

        with open(file_name, "rb") as image_file:
            self.__exif = exif.Image(image_file)

    @property
    def pil_image(self) -> PIL.Image:
        return self.__image

    def add_image_description(self, image_description: ImageDescription):
        self.__exif.set("image_description", image_description.json())
        with open(self.__file_name, "wb") as image_file:
            image_file.write(self.__exif.get_file())

    def add_tag(self, new_tag: Tag) -> None:
        current_description = self.__get_image_description()
        current_description.tags.append(
            TagModel(
                name=new_tag.name,
                x=new_tag.frame.left / self.__image.width,
                y=new_tag.frame.top / self.__image.height,
                w=new_tag.frame.width / self.__image.width,
                h=new_tag.frame.height / self.__image.height,
            )
        )
        self.add_image_description(current_description)

    def remove_tag(self, tag_name) -> None:
        current_description = self.__get_image_description()
        new_description = ImageDescription()
        for tag in current_description.tags:
            if tag.name != tag_name:
                new_description.tags.append(tag)
        self.add_image_description(new_description)

    def get_tags_name(self) -> list[str]:
        try:
            description = ImageDescription.parse_raw(str(self.__exif.image_description))
            return [tag.name for tag in description.tags]
        except Exception:
            return []

    def __get_image_description(self) -> ImageDescription:
        try:
            return ImageDescription.parse_raw(str(self.__exif.image_description))
        except Exception:
            return ImageDescription()

    def get_information(self) -> str:
        return f"# Information\n\n{self.__get_image_description().compact()}"
