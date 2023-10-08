from typing import Literal

import pandas as pd

from .parse_reference import ParseReference
from .recognize_reference import RecognizeReference


class ProcessFile:
    """Process docs file, extract references and citation relationship."""

    def __init__(
        self, docs_df: pd.DataFrame, source: Literal["wos", "cssci", "scopus"]
    ):
        """
        Args:
            docs_df: DataFrame of docs.
            source: Data source. `wos`, `cssci` or `scopus`.
        """
        self._docs_df: pd.DataFrame = docs_df.copy()
        self._source: Literal["wos", "cssci", "scopus"] = source

    @staticmethod
    def _concat_refs(
        cr_field_series: pd.Series,
        source: Literal["wos", "cssci", "scopus"],
    ) -> pd.DataFrame:
        """Concat all parsed references and return dataframe.

        Args:
            cr_field_series: The CR field of docs_df.
            source: Data source. 'wos', 'cssci' or 'scopus'.

        Returns:
            DataFrame of references.
        """

        def parsed_ref_generator():
            for idx in cr_field_series.index:
                cell = cr_field_series.loc[idx]
                if isinstance(cell, str):
                    parsed_refs = ParseReference().parse_ref_cell(cell, source, idx)
                    if parsed_refs is not None:
                        for parsed_ref in parsed_refs:
                            yield parsed_ref

        refs_df = pd.DataFrame(parsed_ref_generator())
        return refs_df

    def extract_reference(self) -> pd.DataFrame:
        """Extract total references and return reference dataframe."""
        cr_field_series = self._docs_df["CR"]
        if self._source == "wos":
            refs_df = self._concat_refs(cr_field_series, "wos")
        elif self._source == "cssci":
            refs_df = self._concat_refs(cr_field_series, "cssci")
        elif self._source == "scopus":
            refs_df = self._concat_refs(cr_field_series, "scopus")
        else:
            raise ValueError("Invalid source type")

        # Maybe duplicate reference in some docs' references
        refs_df.drop_duplicates(ignore_index=True, inplace=True)
        refs_df.insert(0, "ref_index", refs_df.index)
        return refs_df

    @staticmethod
    def _reference2citation(cited_doc_index_series: pd.Series) -> pd.Series:
        citing_doc_index_series = pd.Series(
            [[] for i in range(len(cited_doc_index_series))]
        )
        for doc_index, ref_list in cited_doc_index_series.items():
            if len(ref_list) > 0:
                for ref_index in ref_list:
                    citing_doc_index_series[ref_index].append(doc_index)
        return citing_doc_index_series

    def process_citation(self, refs_df: pd.DataFrame) -> pd.DataFrame:
        """Return citation relationship dataframe."""
        if self._source == "wos":
            self._docs_df["DI"] = self._docs_df["DI"].str.lower()
            refs_df = refs_df.astype({"PY": "int64[pyarrow]"})
            cited_doc_index_series = RecognizeReference.recognize_wos_reference(
                self._docs_df, refs_df
            )

        elif self._source == "cssci":
            self._docs_df["TI"] = self._docs_df["TI"].str.lower()
            refs_df["TI"] = refs_df["TI"].str.lower()
            cited_doc_index_series = RecognizeReference.recognize_cssci_reference(
                self._docs_df, refs_df
            )

        elif self._source == "scopus":
            self._docs_df["TI"] = self._docs_df["TI"].str.lower()
            refs_df["TI"] = refs_df["TI"].str.lower()
            cited_doc_index_series = RecognizeReference.recognize_scopus_reference(
                self._docs_df, refs_df
            )

        else:
            raise ValueError("Invalid source type")

        cited_doc_index_series = cited_doc_index_series.reindex(
            self._docs_df["doc_index"]
        )
        cited_doc_index_series = cited_doc_index_series.apply(
            lambda x: x if isinstance(x, list) else []
        )
        citing_doc_index_series = self._reference2citation(cited_doc_index_series)
        lcr_field = cited_doc_index_series.apply(len)
        lcs_field = citing_doc_index_series.apply(len)
        citation_relationship = pd.DataFrame({"doc_index": self._docs_df.doc_index})
        citation_relationship["cited_doc_index"] = [
            ";".join([str(j) for j in i]) if i else None for i in cited_doc_index_series
        ]
        citation_relationship["citing_doc_index"] = [
            ";".join([str(j) for j in i]) if i else None
            for i in citing_doc_index_series
        ]
        citation_relationship["LCR"] = lcr_field
        citation_relationship["LCS"] = lcs_field
        return citation_relationship