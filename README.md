
# About

# Install

python setup.pt sdist
pip install -e .

# Setup

## Video Extraction

Use the NIST key frame extractor found here:

1 git clone the repository (https://github.com/vitrivr/cineast)

2 git apply java/cineast_patch.txt inside vitrivr/cineast

3 run './gradlew deploy' inside vitrivr/cineast, which will build the binary.

4 note that the location of the binary is in vitrivr/cineast/build/libs

### IMAGE AND VIDEO EXTRACT

All videos and images will be extracted into one directory for quick and uniform access

`python -m aida.ldctools.image --dirs <list of corpus directories with video zip files> --destination <destination image and video directory>`

### VIDEO KEY FRAMES

Extract videos from zip files and pull out key frames.

`python -m aida.media.video --dirs <list of corpus directories with video zip files> --cineast <location of cineast>/build/libs --destination <destination video directory>`

This step places videos, representative_frames and JSON files describing the key frames in the destination directory
#### CONFIG

Create a config.json setting the database information

`{
    "MEDIA_LOCATION":<the destination video directory>,
    "SQLALCHEMY_DATABASE_URI":<database URL>
    "EXTRACTOR_LOCATION":"<cineast directory>/cineast/build/libs"
 }`

### OCR

Languages list is based on languages loaded into the system.

python3.6 -m aida.media.ocr --dirs /opt/AIDACorpora/VideoCorpus/ --destination /opt/AIDACorpora/VideoCorpus/  --languages rus eng

This step places (overwrites) an ocr.txt file in the destination directory.

### Database

Load the Database

~~~
python -m aida.api.textloader --users test/data/users.txt --config config.json
python -m aida.ldcrepo.textloader --dirs <list of corpus directories includin the destination video directory> --config config.json
~~~

Loading the database result should look like the following:

~~~
/Users/x/.virtualenvs/iada-py3/bin/python /Users/x/Documents/workspace/AIDA/python/src/aida/ldcrepo/textloader.py --dirs "/Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E01_AIDA_Seedling_Corpus_V1" "/Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E52_AIDA_Scenario_1_Seedling_Corpus_Part_2" "/Volumes/TOSHIBA EXT/AIDACorpora/VideoCorpus" "/Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0" --config /Users/ericrobertson/Documents/workspace/AIDA/config.json
INFO Scanning directory /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E01_AIDA_Seedling_Corpus_V1
INFO Scanning directory /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E52_AIDA_Scenario_1_Seedling_Corpus_Part_2
INFO Scanning directory /Volumes/TOSHIBA EXT/AIDACorpora/VideoCorpus
INFO Scanning directory /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0
INFO Loading 14 files
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/docs/hypothesis_info.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/docs/media_list.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E01_AIDA_Seedling_Corpus_V1/docs/parent_children.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E52_AIDA_Scenario_1_Seedling_Corpus_Part_2/docs/parent_children.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T101/T101_mini-KB.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T102/T102_mini-KB.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T103/T103_mini-KB.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T101/T101_ent_mentions.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T102/T102_ent_mentions.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T103/T103_ent_mentions.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T101/T101_ent_mentions.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T102/T102_ent_mentions.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/LDC2018E45_AIDA_Scenario_1_Seedling_Annotation_V4.0/data/T103/T103_ent_mentions.tab
INFO Loading /Volumes/TOSHIBA EXT/AIDACorpora/VideoCorpus/json/cineast_multimediaobject.json
INFO Loading complete
~~~

### Back up and Restore Database

TBD

# Run the Server

`python -m aida.runner config.json`

# REST

## Authenticate

All Headers for POST and DELETE requests require an acess token:
"Authorizaion": "Bearer <access token>"

Obtain the Access Token via the following service.

* **URL**

  <root>/api/v1/login

* **Method:**

  POST

* **Data Params**

  Content type of application/json containing user name and password:

  ~~~
  {"username":"admin","password":"pass123"}
  ~~~

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**
    ~~~
   {
     "message": "Logged in as admin",
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Mzk2MzQyMzMsIm5iZiI6MTUzOTYzNDIzMywianRpIjoiOTBhYzkxZDMtYTQ2OS00NDZmLTk1MGQtMzcwNjJlYzM1YzY2IiwiZXhwIjoxNTM5NjM1MTMzLCJpZGVudGl0eSI6ImFkbWluIiwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.g-EC7LtZymixlqTmlmX2iEEMt19YeGvTcWkLv6jqqUQ",
     "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Mzk2MzQyMzQsIm5iZiI6MTUzOTYzNDIzNCwianRpIjoiNGE2N2Y3MjgtYzExZS00YTE4LTg1MmUtODc5Mjk5NzY5OTllIiwiZXhwIjoxNTQyMjI2MjM0LCJpZGVudGl0eSI6ImFkbWluIiwidHlwZSI6InJlZnJlc2gifQ.bkzExp_c6_MlSA47tWiokUKepLcsJeXR10dfAWcdXmE"
   }
    ~~~

* **Error Response:**

  * **Code:** 401 <br />
    **Content:**
    ~~~
    {
      "description": "Invalid credentials",
      "error": "Bad Request",
      "status_code": 401
    }
    ~~~

When a token expires, all service calls will return the following.

    ~~~
    {
        "code":401,
        "error":"invalid_token",
        "error_description":"The access token provided has expired."
    }
    ~~~

Since access tokens expire, a refresh token is used to re-establish the session, obtaining a new access token.


* **URL**

  <root>/api/v1/refresh

* **Method:**

  POST

* **Header**

  Use refresh token instead of access token.

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**
    ~~~
   {
     "message": "Logged in as admin",
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Mzk2MzQyMzMsIm5iZiI6MTUzOTYzNDIzMywianRpIjoiOTBhYzkxZDMtYTQ2OS00NDZmLTk1MGQtMzcwNjJlYzM1YzY2IiwiZXhwIjoxNTM5NjM1MTMzLCJpZGVudGl0eSI6ImFkbWluIiwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.g-EC7LtZymixlqTmlmX2iEEMt19YeGvTcWkLv6jqqUQ"
    ~~~

* **Error Response:**

  * **Code:** 500 <br />


## Entity

List the Entities

* **URL**

  <root>/api/v1/entities

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    [
    {"id": "E779954.00001",
    "kb_id": "E0004",
    "entity_type": "per",
    "description": "298 \\u043e\\u0441\\u0456\\u0431",
    "tree_id": 779954}
    ]
    ~~~

List the Entities without Canonicals

* **URL**

  <root>/api/v1/entities_without_canonical

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    [
     { "id": "E779954.00001",
       "kb_id": "E0004",
       "entity_type": "per",
       "description": "298 \\u043e\\u0441\\u0456\\u0431",
       "tree_id": 779954
      }
    ]
    ~~~

Entity by ID

* **URL**

  <root>/api/v1/entities/id/E779954.00001

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "id": "E779954.00001",
      "kb_id": "E0004",
      "entity_type": "per",
      "description": "298 \\u043e\\u0441\\u0456\\u0431",
      "tree_id": 779954
    }
    ~~~

* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "message" : "Cannot find E779954.00001"
    }
    ~~~

Entities with Mentions not attached to canonical mentions.

* **URL**

  <root>/api/v1/entities_without_canonical

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    [
      {"id": "E779954.00001",
      "kb_id": "E0004",
      "description": "298 \\u043e\\u0441\\u0456\\u0431",
      "entity_type": "per",
      "tree_id": 779954}
    ]
    ~~~

Entities with canonical count.

* **URL**

  <root>/api/v1/entities_with_canonical_count

* **Method:**

  GET

* **Parameters**

   **Optional:**

   `upper_bound=[int]`   return entities with count less or equal to the given upper bound


* **Success Response:**

  Text characters are in unicode format.  The response is a list of list.  Each inner list has three items:
    entity id, entity description, entity type, number of mention, number of non-text media, number of canonical mentions.  The intent is identify which entityies have low counts.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    [
      ["E779954.00001", "298 \\u043e\\u0441\\u0456\\u0431", "per", 4, 3, 2]
    ]
    ~~~


## Entity Mentions

List the Entity Mentions

* **URL**

  <root>/api/v1/entity_mentions

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    [
    {"entity_id": "E779959.00017",
      "id": "EM779959.000179",
      "kb_id": "E0012",
      "level": null,
      "media": {"id": "IC0011SL2", "media_type": "mp4"},
      "mention_type": "per",
      "provenance": "IC0011SL2",
      "text_string": null,
      "justification" : "Igor \"Bes\" Bezler",
      "textoffset_endchar": null,
      "textoffset_startchar": null,
      "tree_id": 779959,
      "status": "Approved"}
    ]
    ~~~

Entity Mention by ID

* **URL**

  <root>/api/v1/entity_mentions?id=EM779959.000179

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
     {"entity_id": "E779959.00017",
      "id": "EM779959.000179",
      "kb_id": "E0012",
      "level": null,
      "media": {"id": "IC0011SL2", "media_type": "mp4"},
      "mention_type": "per",
      "provenance": "IC0011SL2",
      "text_string": null,
      "justification" : "Igor \"Bes\" Bezler",
      "textoffset_endchar": null,
      "textoffset_startchar": null,
      "tree_id": 779959,
      "status": "Approved"
      }
    ~~~

* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "message" : "Cannot find E779954.00017"
    }
    ~~~

Entity Mention by Entity ID

* **URL**

  <root>/api/v1/entity_mentions?entity_id=E779959.00017

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
     [{"entity_id": "E779959.00017",
      "id": "EM779959.000179",
      "kb_id": "E0012",
      "level": null,
      "media": {"id": "IC0011SL2", "media_type": "mp4"},
      "mention_type": "per",
      "provenance": "IC0011SL2",
      "text_string": null,
      "justification" : "Igor \"Bes\" Bezler",
      "textoffset_endchar": null,
      "textoffset_startchar": null,
      "tree_id": 779959,
      "status": "Approved"
      }
      ]
    ~~~



Entity Mention by Count

* **URL**

  <root>/api/v1/entity_mentions_with_canonical_count

* **Method:**

  GET

* **Parameters**

   **Optional:**

   `upper_bound=[int]`    return entities with count less or equal to the given upper bound

* **Success Response:**

  Text characters are in unicode format. The response is a list of list.  Each inner list has three items:
    entity mention id, description, mention type, number of non-text media, number of canonical mentions.  The intent is identify which entities have low counts.

  * **Code:** 200 <br />
    **Content:**

    ~~~
     [["EM779959.000179","Igor \"Bes\" Bezler", "per," 2, 1],
       ...
      ]
    ~~~

Entity Mention by Status

* **URL**

  <root>/api/v1/entity_mentions?status=Approved

* **Method:**

  GET

* **Parameters**

   `status=[Approved | Recommended]`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:**

    ~~~
     [{"entity_id": "E779959.00017",
      "id": "EM779959.000179",
      "kb_id": "E0012",
      "level": null,
      "media": {"id": "IC0011SL2", "media_type": "mp4"},
      "mention_type": "per",
      "provenance": "IC0011SL2",
      "text_string": null,
      "justification" : "Igor \"Bes\" Bezler",
      "textoffset_endchar": null,
      "textoffset_startchar": null,
      "tree_id": 779959,
      "status": "Approved"
      }
      ]
    ~~~

Add/Update Entity Mention (Recommended)

* **URL**

  <root>/api/v1/entity_mentions -H "Content-Type: application/json" -d '{"entity_id":"EM779959.000179", "provenance":"HC00000AJ"}'

* **Data**

   **Required:**

   `entity_id=[string]`
   `provenance=[string]`  REFERENCES Existing provenance.

  **Optional:**
   `id=[string]`  MENTION ID-UPDATE ONLY
   `textoffset_startchar=[string]`
   `textoffset_endchar=[string]`
   `text_string=[string]`
   `status=[string]` UPDATE ONLY
   `level=[string]` UPDATE ONLY
   `tree_id=[string]` UPDATE ONLY
   `kb_id=[string]` UPDATE ONLY

* **Method:**

  POST

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "status": "ok"
      "id": "urn:uuid:89d19497-0112-4bec-b44d-4f526a286df6"
    }
    ~~~

Delete Entity Mention


* **URL**

  <root>/api/v1/entity_mentions?id=urn:uuid:89d19497-0112-4bec-b44d-4f526a286df6

* **Data**

   **Required:**

   `id=[string]` Entity mention ID

   **Optional:**

   `force=[true | false]`

* **Method:**

  DELETE

* **Behavior:**

  Cannot delete mentions that are Approved or have Canonicals.  The force option overrides both conditions.
  With the force option, associated canonicals are also removed.

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "status": "ok"
      "id": "urn:uuid:89d19497-0112-4bec-b44d-4f526a286df6"
    }
    ~~~

* **ERROR Response:**

* **Code:** 400 <br />
    **Content:**

    ~~~
    {"message": "Cannot find entity mention urn:uuid:89d19497-0112-4bec-b44d-4f526a286df6"}
    ~~~

* **Code:** 400 <br />
    **Content:**

    ~~~
    {"message": "Cannot delete approved entity mention urn:uuid:89d19497-0112-4bec-b44d-4f526a286df6"}
    ~~~

## Parent Child

List Parent Child Detail

* **URL**

  <root>/api/v1/parent_child_detail

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**
    ~~~

    [{"child_file": "HC0000077.mp4.ldcc",
      "download_date": "2017-10-16T12:18:09",
      "dtype": "vid",
      "id": "urn:uuid:cbb9269f-ac65-4fa4-98de-99b41b7a0922",
      "parent_uid": "IC0011SNF",
      "rel_pos": 1,
      "unwrapped_md5": "1b7e854b5865f8bc8f2f92e854f9e265",
      "url": "https://www.youtube.com/watch?v=BbyZYgSXdyw",
      "wrapped_md5": "6e49088d20c445d106b4ae1cedfa9ed0",
      "segment_count": 102
      }
    ]
    ~~~

List Parent Child Detail for a specific Entity Mention

* **URL**

  <root>/api/v1/parent_child_detail/provenance/IC0019N7Y

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**
    ~~~

    [{"child_file": "IC0019N7Y.mp4.ldcc",
      "download_date": "2017-10-16T12:18:09",
      "dtype": "vid",
      "id": ""urn:uuid:56db5e32-feb4-4b55-ab6a-9d05fdf2c516",
      "parent_uid": "IC0015NC8",
      "rel_pos": 1,
      "unwrapped_md5": "0344f5e50edeaab49006d532b297e69d",
      "url": "https://www.youtube.com/embed/T34AB6CImTE?rel=0",
      "wrapped_md5": "31e5f892cc70342b7937373349c86b9e",
      "segment_count": 102}
    ]
    ~~~


Parent Child Details for a File

* **URL**

  <root>/api/v1/parent_child_detail/file/IC0019N7Y.mp4.ldcc

* **Method:**

  GET

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**
    ~~~

    [{"child_file": "IC0019N7Y.mp4.ldcc",
      "download_date": "2017-10-16T12:18:09",
      "dtype": "vid",
      "id": ""urn:uuid:56db5e32-feb4-4b55-ab6a-9d05fdf2c516",
      "parent_uid": "IC0015NC8",
      "rel_pos": 1,
      "unwrapped_md5": "0344f5e50edeaab49006d532b297e69d",
      "url": "https://www.youtube.com/embed/T34AB6CImTE?rel=0",
      "wrapped_md5": "31e5f892cc70342b7937373349c86b9e",
      "segment_count": 102}
    ]
    ~~~


## Canonical

Save a canonical

* **URL**

  <root>/api/v1/canonical_mentions' -H "Content-Type: application/json" -d '{"entity_mention_id":"EM779959.000179", "child_file":"HC00000AJ.jpg.ldcc", "frame_number":100}'

* **Data**

   **Required:**

   `entity_mention_id=[string]`
   `child_file=[string]`

  **Required for Video:**

   `frame_number=[numeric]`
   `frame_time=[numeric millseconds]`
   `bounding_box=[string format upper x, upper y, lower x, lower y]`

  **Required for PDF:**

   `page_number=[numeric millseconds]`

  **Required for Image:**

   `bounding_box=[string format upper x, upper y, lower x, lower y]`

* **Method:**

  POST

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "status": "ok"
    }
    ~~~

List Canonical Mentions

* **URL**

  <root>/api/v1/canonical_mentions

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

    ~~~
     [{"bounding_box": null,
     "child_file": "HC00000AJ.jpg.ldcc",
     "entity_mention_id": "EM779959.000179",
     "frame_number": 100,
     "frame_time": null,
     "id": "urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784",
     "page_number": null,
     "user_id": "person123",
     "record_time": "2018-10-15T13:45:52"}
     ]
     ~~~

List Canonical Mentions for File

* **URL**

  <root>/api/v1/canonical_mentions/media/HC00000AJ.jpg.ldcc

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

    ~~~
     [{"bounding_box": null,
     "child_file": "HC00000AJ.jpg.ldcc",
     "entity_mention_id": "EM779959.000179",
     "frame_number": 100,
     "frame_time": null,
     "id": "urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784",
     "page_number": null,
     "user_id": "person123",
     "record_time": "2018-10-15T13:45:52"}
     ]
     ~~~

Canonical Mention by ID

* **URL**

  <root>/api/v1/canonical_mentions/urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

     ~~~
     {"bounding_box": null,
     "child_file": "HC00000AJ.jpg.ldcc",
     "entity_mention_id": "EM779959.000179",
     "frame_number": 100,
     "frame_time": null,
     "id": "urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784",
     "page_number": null,
     "user_id": "person123",
     "record_time": "2018-10-15T13:45:52"}
     ~~~

* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "message" : "Cannot find urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784"
    }
    ~~~

Delete Canonical Mention by ID

* **URL**

  <root>/api/v1/canonical_mentions/urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784

* **Method:**

  DELETE

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

     ~~~
     {
       "status": "ok"
     }
     ~~~

* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "message" : "Cannot find urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784"
    }
    ~~~


Canonical Mentions for Entity ID

* **URL**

  <root>/api/v1/canonical_mentions/entity/E779959.00017

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

     ~~~
     [
     {"bounding_box": null,
     "child_file": "HC00000AJ.jpg.ldcc",
     "entity_mention_id": "EM779959.000179",
     "frame_number": 100,
     "frame_time": null,
     "id": "urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784",
     "page_number": null,
     "user_id": "person123",
     "record_time": "2018-10-15T13:45:52"}
     ]
     ~~~

* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    []
    ~~~

Canonical Mentions for Entity Mention ID

* **URL**

  <root>/api/v1/canonical_mentions/entity_mention/E779959.000179

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

     ~~~
     [
     {"bounding_box": null,
     "child_file": "HC00000AJ.jpg.ldcc",
     "entity_mention_id": "EM779959.000179",
     "frame_number": 100,
     "frame_time": null,
     "id": "urn:uuid:efd39c0b-eddc-430f-a0a4-c96d8a2c7784",
     "page_number": null,
     "user_id": "person123",
     "record_time": "2018-10-15T13:45:52"}
     ]
     ~~~

* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    []
    ~~~


## Media

Get Media Frames

* **URL**

  <root>/api/v1//api/v1/media?file_id=IC0011SL2.mp4.ldcc&frame_number=1

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**
     Stream of Bytes

* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "message": "Cannot find /Volumes/TOSHIBA EXT/AIDACorpora/VideoCorpus/IC0011SL2.mp4.ldxc"
    }
    ~~~

Get All

* **URL**

  <root>/api/v1//api/v1/media

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    [{"id": "IC0011SL2", "media_type": "mp4"},...]

* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    []
    ~~~

## Segments

Get Segment for File

* **URL**

  <root>/api/v1//api/v1//segments/IC0011SL2.mp4.ldcc

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

    ~~~
    [
    {
        "file_id": "IC0011SL2.mp4.ldcc",
        "id": "urn:uuid:4dcb241c-2531-487f-b0cd-646ab9e58aed",
        "segment_end": 194,
        "segment_end_abs": 6.472367,
        "segment_number": 1,
        "segment_start": 1,
        "segment_start_abs": 0.0,
        "representative_frame_number": 108,
        "representative_frame_time": 6.472367,
        "frame_file_name": "representative_frames/v_2WrJ79KLbMbIZsGv/v_2WrJ79KLbMbIZsGv_1.png",
        "segment_objects": [{
           "bounding_box": "122.859375,56.203125,172.859375,106.203125",
           "id": "urn:uuid:37b8ad3a-c26f-47b1-be9e-62aa29b11405",
           "object_type": "fac",
           "segment_id": "urn:uuid:e4e84f35-8926-40bf-bc17-1beb355acb6b"
        }
        ],
        "segment_texts": [{
           "id": "urn:uuid:f876d5bd-4f79-4b54-bf85-85f1ea437ee6",
            "language": "eng",
            "text": "Strobe Talbet Blames Russia",
            "text_type": "inf"
        }
        ]
    ]
    ~~~


* **Error Response:**

   * **Code:** 200 <br />
    **Content:**

    ~~~
    []
    ~~~


Get Segment

* **URL**

  <root>/api/v1/api/v1/segment

* **Method:**

  GET

* **URL Params:**

 `segment_id=<segment id>`

 OR

 `file_id=<comment_id>&frame_no=<frame number>`

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

    ~~~
    {
        "file_id": "IC0011SL2.mp4.ldcc",
        "id": "urn:uuid:4dcb241c-2531-487f-b0cd-646ab9e58aed",
        "segment_end": 194,
        "segment_end_abs": 6.472367,
        "segment_number": 1,
        "segment_start": 1,
        "segment_start_abs": 0.0,
        "representative_frame_number": 108
        "frame_file_name": "representative_frames/v_2WrJ79KLbMbIZsGv/v_2WrJ79KLbMbIZsGv_1.png",
                "segment_objects": [{
           "bounding_box": "122.859375,56.203125,172.859375,106.203125",
           "id": "urn:uuid:37b8ad3a-c26f-47b1-be9e-62aa29b11405",
           "object_type": "fac",
           "segment_id": "urn:uuid:e4e84f35-8926-40bf-bc17-1beb355acb6b"
        }
        ],
        "segment_texts": [{
           "id": "urn:uuid:f876d5bd-4f79-4b54-bf85-85f1ea437ee6",
            "language": "eng",
            "text": "Strobe Talbet Blames Russia",
            "text_type": "inf"
        }
        ]
    }
    ~~~


Get Segments for Text

* **URL**

  <root>/api/v1//api/v1/segments_text/Talbet+Blames

* **Method:**

  GET

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

    ~~~
     [
    {
        "file_id": "IC0011SL2.mp4.ldcc",
        "id": "urn:uuid:4dcb241c-2531-487f-b0cd-646ab9e58aed",
        "segment_end": 194,
        "segment_end_abs": 6.472367,
        "segment_number": 1,
        "segment_start": 1,
        "segment_start_abs": 0.0,
        "representative_frame_number": 108
        "frame_file_name": "representative_frames/v_2WrJ79KLbMbIZsGv/v_2WrJ79KLbMbIZsGv_1.png",
        "segment_objects": [{
           "bounding_box": "122.859375,56.203125,172.859375,106.203125",
           "id": "urn:uuid:37b8ad3a-c26f-47b1-be9e-62aa29b11405",
           "object_type": "fac",
           "segment_id": "urn:uuid:e4e84f35-8926-40bf-bc17-1beb355acb6b"
        }
        ],
        "segment_texts": [{
           "id": "urn:uuid:f876d5bd-4f79-4b54-bf85-85f1ea437ee6",
            "language": "eng",
            "text": "Strobe Talbet Blames Russia",
            "text_type": "inf"
        }
        ]
    }
    ]
    ~~~

Get Segments for Object

Find all segments associated to the object

* **URL**

  <root>/api/v1//api/v1/segments_objects/urn:uuid:37b8ad3a-c26f-47b1-be9e-62aa29b11405

* **Method:**

  GET

* **Parameters**

   **Optional:**

   `match_strength=[float]`   return values with given strenth or greater

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

    ~~~
    [
     [
      {
       "bounding_box": "122.859375,56.203125,172.859375,106.203125",
       "id": "urn:uuid:37b8ad3a-c26f-47b1-be9e-62aa29b11405",
       "object_type": "fac",
       "segment_id": "urn:uuid:e4e84f35-8926-40bf-bc17-1beb355acb6b"
      },
      1.42465,
      {
       "file_id": "IC0011SL2.mp4.ldcc",
       "frame_file_name": "representative_frames/v_2WrJ79KLbMbIZsGv/v_2WrJ79KLbMbIZsGv_2.png",
       "id": "urn:uuid:e4e84f35-8926-40bf-bc17-1beb355acb6b",
       "is_stream": true,
       "representative_frame_number": 198,
       "representative_frame_time": 198.0,
       "segment_end": 200,
       "segment_end_abs": 6.6723666,
       "segment_number": 2,
       "segment_objects": [
        {
         "bounding_box": "122.859375,56.203125,172.859375,106.203125",
         "id": "urn:uuid:37b8ad3a-c26f-47b1-be9e-62aa29b11405",
         "object_type": "fac",
         "segment_id": "urn:uuid:e4e84f35-8926-40bf-bc17-1beb355acb6b"
        }
       ],
       "segment_start": 195,
       "segment_start_abs": 6.473,
       "segment_texts": []
      }
     ],
     [
      {
       "bounding_box": "227.859375,140.203125,277.859375,190.203125",
       "id": "urn:uuid:b31ba43c-698d-4611-ad0b-f2d8095b8bcb",
       "object_type": "fac",
       "segment_id": "urn:uuid:0b692f04-6274-4dbd-9b80-4ff6af127b60"
      },
      {
       "file_id": "IC0011SL2.mp4.ldcc",
       "frame_file_name": "representative_frames/v_2WrJ79KLbMbIZsGv/v_2WrJ79KLbMbIZsGv_22.png",
       "id": "urn:uuid:0b692f04-6274-4dbd-9b80-4ff6af127b60",
       "is_stream": true,
       "representative_frame_number": 1795,
       "representative_frame_time": 1795.0,
       "segment_end": 1800,
       "segment_end_abs": 60.05937,
       "segment_number": 22,
       "segment_objects": [
        {
         "bounding_box": "227.859375,140.203125,277.859375,190.203125",
         "id": "urn:uuid:b31ba43c-698d-4611-ad0b-f2d8095b8bcb",
         "object_type": "fac",
         "segment_id": "urn:uuid:0b692f04-6274-4dbd-9b80-4ff6af127b60"
        }
       ],
       "segment_start": 1789,
       "segment_start_abs": 59.659,
       "segment_texts": [
        {
         "id": "urn:uuid:4abcc1e3-a74c-4cd1-bfae-6a7aded64c28",
         "language": "eng",
         "text": "Strobe Talbet Blames Russia",
         "text_type": "inf"
        }
       ]
      }
     ]
    ]
    ~~~

Get Index for Video

* **URL**

  <root>/api/v1/api/v1/index

* **Method:**

  POST

* **Data**

   **Required:**
   Multiform data:

   video = video file stream (e.g. @./5136166715.mp4)
   image = image file stream (e.g. @./5136166715.png)

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

    Matches
    ~~~
   {
    "matches": {
        "v_r6tk4SzEPrlCegAl_1.png": {
            "file_name": "5136166715.mp4",
            "segment_number": 1,
            "start": 1,
            "end": 82,
            "start_abs": 0,
            "end_abs": 2.7353666,
            "representative_frame_number": 32,
            "frame_file_name": "v_r6tk4SzEPrlCegAl_1.png"
        }
    }
}
    ~~~


## Comments

Get Comments

* **URL**

  <root>/api/v1//api/v1/comment/

* **Method:**

  GET

* **URL Params:**

 `segment_id=<segment id>`

 OR

 `id=<comment_id>`

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

   If by comment id, then:
    ~~~
   {
   "comment": "Recommended Test",
   "entity_mention_id": "EM779959.000179",
   "id": "urn:uuid:b40479d6-5844-4324-a60f-16edf1ff5dac",
   "segment_id": "urn:uuid:a666ff0e-f038-4df9-ad84-bc4e977b28f0",
   "user_id": "test_user",
   "record_time": "2018-10-15T13:45:52"
   }
    ~~~

     If by segment id, then:
    ~~~
   [
   {
   "comment": "Recommended Test",
   "entity_mention_id": "EM779959.000179",
   "id": "urn:uuid:b40479d6-5844-4324-a60f-16edf1ff5dac",
   "segment_id": "urn:uuid:a666ff0e-f038-4df9-ad84-bc4e977b28f0",
   "user_id": "test_user"
   },
   ...
   ]
    ~~~

* **Error Response:**

   * **Code:** 400 <br />
    **Content:**

    ~~~
    []
    ~~~

Create Segment Comment

* **URL**

  <root>/api/v1/api/v1/comment

* **Method:**

  POST

* **Data Params:**

  Content type of application/json containing user name and password:

  ~~~
  {"entity_mention_id":"xxx","segment_id":"yyy","comment":"text",}
  ~~~

* **Success Response:**

 * **Code:** 200 <br />
    **Content:**

    ~~~
    {"status": "ok", "id": "urn:uuid:b40479d6-5844-4324-a60f-16edf1ff5dac"}
    ~~~



Delete Segment Comment


* **URL**

  <root>/api/v1/comment?id=urn:uuid:89d19497-0112-4bec-b44d-4f526a286df6"

* **Data**

   **Required:**

   `id=[string]` Segment Comment ID

* **Method:**

  DELETE

* **Success Response:**

  Text characters are in unicode format.

  * **Code:** 200 <br />
    **Content:**

    ~~~
    {
      "status": "ok"
    }
    ~~~

* **ERROR Response:**

* **Code:** 400 <br />
    **Content:**

    ~~~
    {"message": "Invalid comment id urn:uuid:89d19497-0112-4bec-b44d-4f526a286df6"}
    ~~~

* **Code:** 200 <br />
    **Content:**

    ~~~
     {
      "status": "failed"
    }
    ~~~
