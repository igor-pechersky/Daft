from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daft.recordbatch import MicroPartition


@dataclass(frozen=True)
class DataFramePreview:
    """A class containing all the metadata/data required to preview a dataframe."""

    preview_partition: MicroPartition | None
    dataframe_num_rows: int | None
