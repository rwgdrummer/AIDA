# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from flask_sqlalchemy import SQLAlchemy
from nearpy.storage import Storage
db = SQLAlchemy()

class IndexModel(db.Model):
    __tablename__ = 'kb'
    id = db.Column(db.String(10), primary_key=True)
    hash_name = db.Column(db.String(64), unique=False, nullable=False)
    category = db.Column(db.String(40), unique=False, nullable=False)
    handle = db.Column(db.String(120), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=False)
    relative_mentions = db.relationship('RelativeMention', backref='kb', lazy=True)
    entity_mentions = db.relationship('EntityMention', backref='kb', lazy=True)

    def __repr__(self):
        return '<KB %r>' % self.id

class SQLStorageStorage(Storage):
    """ Storage using QAL. """

    def __init__(self, redis_object):
        """ Uses specified redis object for storage. """
        self.redis_object = redis_object

    def store_vector(self, hash_name, bucket_key, v, data):
        """
        Stores vector and JSON-serializable data in bucket with specified key.
        """
        redis_key = self._format_redis_key(hash_name, bucket_key)

        val_dict = {}

        # Depending on type (sparse or not) fill value dict
        if scipy.sparse.issparse(v):
            # Make sure that we are using COO format (easy to handle)
            if not scipy.sparse.isspmatrix_coo(v):
                v = scipy.sparse.coo_matrix(v)

            # Construct list of [index, value] items,
            # one for each non-zero element of the sparse vector
            encoded_values = []

            for k in range(v.data.size):
                row_index = v.row[k]
                value = v.data[k]
                encoded_values.append([int(row_index), value])

            val_dict['sparse'] = 1
            val_dict['nonzeros'] = encoded_values
            val_dict['dim'] = v.shape[0]
        else:
            # Make sure it is a 1d vector
            v = numpy.reshape(v, v.shape[0])
            val_dict['vector'] = v.tostring()

        val_dict['dtype'] = v.dtype.name

        # Add data if set
        if data is not None:
            val_dict['data'] = data

        # Push JSON representation of dict to end of bucket list
        self.redis_object.rpush(redis_key, pickle.dumps(val_dict, protocol=2))

    def _format_redis_key(self, hash_name, bucket_key):
        return '{}{}'.format(self._format_hash_prefix(hash_name), bucket_key)

    def _format_hash_prefix(self, hash_name):
        return "nearpy_{}_".format(hash_name)

    def get_all_bucket_keys(self, hash_name):
        prefix_len = len(self._format_hash_prefix(hash_name))
        return [bytes(key).decode()[prefix_len:]
                for key in self._iter_bucket_keys(hash_name)]

    def _iter_bucket_keys(self, hash_name):
        pattern = "{}*".format(self._format_hash_prefix(hash_name))
        return self.redis_object.scan_iter(pattern)

    def _get_bucket_rows(self, hash_name, bucket_key):
        redis_key = self._format_redis_key(hash_name, bucket_key)
        return self.redis_object.lrange(redis_key, 0, -1)

    def delete_vector(self, hash_name, bucket_keys, data):
        """
        Deletes vector and JSON-serializable data in buckets with specified keys.
        """
        with self.redis_object.pipeline() as pipeline:
            for key in bucket_keys:
                redis_key = self._format_redis_key(hash_name, key)
                rows = [(row, pickle.loads(row).get('data'))
                        for row in self._get_bucket_rows(hash_name, key)]
                for _, id_data in rows:
                    if id_data == data:
                        break
                else:
                    # Deleted data is not present in this bucket
                    continue
                pipeline.delete(redis_key)
                pipeline.rpush(redis_key, *(row for row, id_data in rows
                                            if id_data != data))
            pipeline.execute()

    def get_bucket(self, hash_name, bucket_key):
        """
        Returns bucket content as list of tuples (vector, data).
        """
        results = []
        for row in self._get_bucket_rows(hash_name, bucket_key):
            val_dict = pickle.loads(row)
            # Depending on type (sparse or not) reconstruct vector
            if 'sparse' in val_dict:

                # Fill these for COO creation
                row = []
                col = []
                data = []

                # For each non-zero element, append values
                for e in val_dict['nonzeros']:
                    row.append(e[0])  # Row index
                    data.append(e[1])  # Value
                    col.append(0)  # Column index (always 0)

                # Create numpy arrays for COO creation
                coo_row = numpy.array(row, dtype=numpy.int32)
                coo_col = numpy.array(col, dtype=numpy.int32)
                coo_data = numpy.array(data)

                # Create COO sparse vector
                vector = scipy.sparse.coo_matrix((coo_data, (coo_row, coo_col)), shape=(val_dict['dim'], 1))

            else:
                vector = numpy.fromstring(val_dict['vector'],
                                          dtype=val_dict['dtype'])

            # Add data to result tuple, if present
            results.append((vector, val_dict.get('data')))

        return results

    def clean_buckets(self, hash_name):
        """
        Removes all buckets and their content for specified hash.
        """
        bucket_keys = self._iter_bucket_keys(hash_name)
        self.redis_object.delete(*bucket_keys)

    def clean_all_buckets(self):
        """
        Removes all buckets from all hashes and their content.
        """
        bucket_keys = self.redis_object.keys(pattern='nearpy_*')
        if len(bucket_keys) > 0:
            self.redis_object.delete(*bucket_keys)

    def store_hash_configuration(self, lshash):
        """
        Stores hash configuration
        """
        self.redis_object.set(lshash.hash_name+'_conf', pickle.dumps(lshash.get_config()))

    def load_hash_configuration(self, hash_name):
        """
        Loads and returns hash configuration
        """
        conf = self.redis_object.get(hash_name+'_conf')

        return pickle.loads(conf) if conf is not None else None
