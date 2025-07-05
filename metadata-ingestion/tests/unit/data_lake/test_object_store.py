import unittest
from unittest.mock import MagicMock

from datahub.ingestion.source.data_lake_common.object_store import (
    ABSObjectStore,
    GCSObjectStore,
    S3ObjectStore,
    get_abs_external_url,
    get_gcs_external_url,
    get_object_key,
    get_object_store_bucket_name,
    get_object_store_for_uri,
    get_s3_external_url,
)


class TestS3ObjectStore(unittest.TestCase):
    """Tests for the S3ObjectStore implementation."""

    def test_is_uri(self):
        """Test the is_uri method with various URIs."""
        self.assertTrue(S3ObjectStore.is_uri("s3://bucket/path"))
        self.assertTrue(S3ObjectStore.is_uri("s3n://bucket/path"))
        self.assertTrue(S3ObjectStore.is_uri("s3a://bucket/path"))
        self.assertFalse(S3ObjectStore.is_uri("gs://bucket/path"))
        self.assertFalse(
            S3ObjectStore.is_uri("abfss://container@account.dfs.core.windows.net/path")
        )
        self.assertFalse(S3ObjectStore.is_uri("file:///path/to/file"))

    def test_get_prefix(self):
        """Test the get_prefix method."""
        self.assertEqual(S3ObjectStore.get_prefix("s3://bucket/path"), "s3://")
        self.assertEqual(S3ObjectStore.get_prefix("s3n://bucket/path"), "s3n://")
        self.assertEqual(S3ObjectStore.get_prefix("s3a://bucket/path"), "s3a://")
        self.assertIsNone(S3ObjectStore.get_prefix("gs://bucket/path"))

    def test_strip_prefix(self):
        """Test the strip_prefix method."""
        self.assertEqual(S3ObjectStore.strip_prefix("s3://bucket/path"), "bucket/path")
        self.assertEqual(S3ObjectStore.strip_prefix("s3n://bucket/path"), "bucket/path")
        self.assertEqual(S3ObjectStore.strip_prefix("s3a://bucket/path"), "bucket/path")

        # Should raise ValueError for non-S3 URIs
        with self.assertRaises(ValueError):
            S3ObjectStore.strip_prefix("gs://bucket/path")

    def test_get_bucket_name(self):
        """Test the get_bucket_name method."""
        self.assertEqual(S3ObjectStore.get_bucket_name("s3://bucket/path"), "bucket")
        self.assertEqual(
            S3ObjectStore.get_bucket_name("s3n://my-bucket/path/to/file"), "my-bucket"
        )
        self.assertEqual(
            S3ObjectStore.get_bucket_name("s3a://bucket.name/file.txt"), "bucket.name"
        )

        # Should raise ValueError for non-S3 URIs
        with self.assertRaises(ValueError):
            S3ObjectStore.get_bucket_name("gs://bucket/path")

    def test_get_object_key(self):
        """Test the get_object_key method."""
        self.assertEqual(S3ObjectStore.get_object_key("s3://bucket/path"), "path")
        self.assertEqual(
            S3ObjectStore.get_object_key("s3://bucket/path/to/file.txt"),
            "path/to/file.txt",
        )
        self.assertEqual(S3ObjectStore.get_object_key("s3://bucket/"), "")
        self.assertEqual(S3ObjectStore.get_object_key("s3://bucket"), "")

        # Should raise ValueError for non-S3 URIs
        with self.assertRaises(ValueError):
            S3ObjectStore.get_object_key("gs://bucket/path")


class TestGCSObjectStore(unittest.TestCase):
    """Tests for the GCSObjectStore implementation."""

    def test_is_uri(self):
        """Test the is_uri method with various URIs."""
        self.assertTrue(GCSObjectStore.is_uri("gs://bucket/path"))
        self.assertFalse(GCSObjectStore.is_uri("s3://bucket/path"))
        self.assertFalse(
            GCSObjectStore.is_uri("abfss://container@account.dfs.core.windows.net/path")
        )

    def test_get_prefix(self):
        """Test the get_prefix method."""
        self.assertEqual(GCSObjectStore.get_prefix("gs://bucket/path"), "gs://")
        self.assertIsNone(GCSObjectStore.get_prefix("s3://bucket/path"))

    def test_strip_prefix(self):
        """Test the strip_prefix method."""
        self.assertEqual(GCSObjectStore.strip_prefix("gs://bucket/path"), "bucket/path")

        # Should raise ValueError for non-GCS URIs
        with self.assertRaises(ValueError):
            GCSObjectStore.strip_prefix("s3://bucket/path")

    def test_get_bucket_name(self):
        """Test the get_bucket_name method."""
        self.assertEqual(GCSObjectStore.get_bucket_name("gs://bucket/path"), "bucket")
        self.assertEqual(
            GCSObjectStore.get_bucket_name("gs://my-bucket/path/to/file"), "my-bucket"
        )

        # Should raise ValueError for non-GCS URIs
        with self.assertRaises(ValueError):
            GCSObjectStore.get_bucket_name("s3://bucket/path")

    def test_get_object_key(self):
        """Test the get_object_key method."""
        self.assertEqual(GCSObjectStore.get_object_key("gs://bucket/path"), "path")
        self.assertEqual(
            GCSObjectStore.get_object_key("gs://bucket/path/to/file.txt"),
            "path/to/file.txt",
        )
        self.assertEqual(GCSObjectStore.get_object_key("gs://bucket/"), "")
        self.assertEqual(GCSObjectStore.get_object_key("gs://bucket"), "")

        # Should raise ValueError for non-GCS URIs
        with self.assertRaises(ValueError):
            GCSObjectStore.get_object_key("s3://bucket/path")


class TestABSObjectStore(unittest.TestCase):
    """Tests for the ABSObjectStore implementation."""

    def test_is_uri(self):
        """Test the is_uri method with various URIs."""
        self.assertTrue(
            ABSObjectStore.is_uri("abfss://container@account.dfs.core.windows.net/path")
        )
        self.assertFalse(ABSObjectStore.is_uri("s3://bucket/path"))
        self.assertFalse(ABSObjectStore.is_uri("gs://bucket/path"))

    def test_get_prefix(self):
        """Test the get_prefix method."""
        self.assertEqual(
            ABSObjectStore.get_prefix(
                "abfss://container@account.dfs.core.windows.net/path"
            ),
            "abfss://",
        )
        self.assertIsNone(ABSObjectStore.get_prefix("s3://bucket/path"))

    def test_strip_prefix(self):
        """Test the strip_prefix method."""
        self.assertEqual(
            ABSObjectStore.strip_prefix(
                "abfss://container@account.dfs.core.windows.net/path"
            ),
            "container@account.dfs.core.windows.net/path",
        )

        # Should raise ValueError for non-ABS URIs
        with self.assertRaises(ValueError):
            ABSObjectStore.strip_prefix("s3://bucket/path")

    def test_get_bucket_name(self):
        """Test the get_bucket_name method."""
        self.assertEqual(
            ABSObjectStore.get_bucket_name(
                "abfss://container@account.dfs.core.windows.net/path"
            ),
            "container",
        )

        # Should raise ValueError for non-ABS URIs
        with self.assertRaises(ValueError):
            ABSObjectStore.get_bucket_name("s3://bucket/path")

    def test_get_object_key(self):
        """Test the get_object_key method."""
        self.assertEqual(
            ABSObjectStore.get_object_key(
                "abfss://container@account.dfs.core.windows.net/path"
            ),
            "path",
        )
        self.assertEqual(
            ABSObjectStore.get_object_key(
                "abfss://container@account.dfs.core.windows.net/path/to/file.txt"
            ),
            "path/to/file.txt",
        )

        # Should raise ValueError for non-ABS URIs
        with self.assertRaises(ValueError):
            ABSObjectStore.get_object_key("s3://bucket/path")


class TestUtilityFunctions(unittest.TestCase):
    """Tests for the utility functions in object_store module."""

    def test_get_object_store_for_uri(self):
        """Test the get_object_store_for_uri function."""
        self.assertEqual(get_object_store_for_uri("s3://bucket/path"), S3ObjectStore)
        self.assertEqual(get_object_store_for_uri("gs://bucket/path"), GCSObjectStore)
        self.assertEqual(
            get_object_store_for_uri(
                "abfss://container@account.dfs.core.windows.net/path"
            ),
            ABSObjectStore,
        )
        self.assertIsNone(get_object_store_for_uri("file:///path/to/file"))

    def test_get_object_store_bucket_name(self):
        """Test the get_object_store_bucket_name function."""
        self.assertEqual(get_object_store_bucket_name("s3://bucket/path"), "bucket")
        self.assertEqual(get_object_store_bucket_name("gs://bucket/path"), "bucket")
        self.assertEqual(
            get_object_store_bucket_name(
                "abfss://container@account.dfs.core.windows.net/path"
            ),
            "container",
        )

        # Should raise ValueError for unsupported URIs
        with self.assertRaises(ValueError):
            get_object_store_bucket_name("file:///path/to/file")

    def test_get_object_key(self):
        """Test the get_object_key function."""
        self.assertEqual(get_object_key("s3://bucket/path"), "path")
        self.assertEqual(
            get_object_key("gs://bucket/path/to/file.txt"), "path/to/file.txt"
        )
        self.assertEqual(
            get_object_key("abfss://container@account.dfs.core.windows.net/path"),
            "path",
        )

        # Should raise ValueError for unsupported URIs
        with self.assertRaises(ValueError):
            get_object_key("file:///path/to/file")


class TestObjectStoreToplevelFunctions(unittest.TestCase):
    """Tests for top-level functions in the object_store module."""

    def test_get_s3_external_url(self):
        """Test the get_s3_external_url static method."""
        mock_table_data = MagicMock()
        mock_table_data.table_path = "s3://bucket/path/to/file.txt"

        # Test with default region
        self.assertEqual(
            get_s3_external_url(mock_table_data),
            "https://us-east-1.console.aws.amazon.com/s3/buckets/bucket?prefix=path/to/file.txt",
        )

        # Test with custom region
        self.assertEqual(
            get_s3_external_url(mock_table_data, "us-west-2"),
            "https://us-west-2.console.aws.amazon.com/s3/buckets/bucket?prefix=path/to/file.txt",
        )

        # Test with non-S3 URI
        mock_table_data.table_path = "gs://bucket/path"
        self.assertIsNone(get_s3_external_url(mock_table_data))

    def test_get_gcs_external_url(self):
        """Test the get_gcs_external_url static method."""
        mock_table_data = MagicMock()
        mock_table_data.table_path = "gs://bucket/path/to/file.txt"

        self.assertEqual(
            get_gcs_external_url(mock_table_data),
            "https://console.cloud.google.com/storage/browser/bucket/path/to/file.txt",
        )

        # Test with non-GCS URI
        mock_table_data.table_path = "s3://bucket/path"
        self.assertIsNone(get_gcs_external_url(mock_table_data))

    def test_get_abs_external_url(self):
        """Test the get_abs_external_url static method."""
        mock_table_data = MagicMock()
        mock_table_data.table_path = (
            "abfss://container@account.dfs.core.windows.net/path/to/file.txt"
        )

        self.assertEqual(
            get_abs_external_url(mock_table_data),
            "https://portal.azure.com/#blade/Microsoft_Azure_Storage/ContainerMenuBlade/overview/storageAccountId/account/containerName/container",
        )

        # Test with non-ABS URI
        mock_table_data.table_path = "s3://bucket/path"
        self.assertIsNone(get_abs_external_url(mock_table_data))

    def test_get_external_url(self):
        """Test the get_external_url method."""
        mock_table_data = MagicMock()

        # Test S3 adapter
        mock_table_data.table_path = "s3://bucket/path/to/file.txt"
        self.assertEqual(
            get_s3_external_url(mock_table_data, "us-west-2"),
            "https://us-west-2.console.aws.amazon.com/s3/buckets/bucket?prefix=path/to/file.txt",
        )

        # Test GCS adapter
        mock_table_data.table_path = "gs://bucket/path/to/file.txt"
        self.assertEqual(
            get_gcs_external_url(mock_table_data),
            "https://console.cloud.google.com/storage/browser/bucket/path/to/file.txt",
        )

        # Test ABS adapter
        mock_table_data.table_path = (
            "abfss://container@account.dfs.core.windows.net/path/to/file.txt"
        )
        self.assertEqual(
            get_abs_external_url(mock_table_data),
            "https://portal.azure.com/#blade/Microsoft_Azure_Storage/ContainerMenuBlade/overview/storageAccountId/account/containerName/container",
        )


if __name__ == "__main__":
    unittest.main()
