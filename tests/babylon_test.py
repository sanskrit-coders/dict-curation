import logging
import os

from dict_curation import babylon


test_babylon = os.path.join(os.path.dirname(__file__), "test.babylon")


def test_get_existing_definitions():
    definitions = babylon.get_definitions(test_babylon)
    headword = 'આપોશાન'
    assert headword in definitions
    logging.info(definitions[headword])


