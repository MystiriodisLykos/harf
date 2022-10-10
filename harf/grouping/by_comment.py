from harf_serde import (
    RequestF,
    EntryF,
    LogF,
    FHar,
    Page,
    PageTimings,
)


def icomment_requests(har: FHar) -> FHar:
    if isinstance(har, LogF):
        pages = []
        entries = []
        for entry in har.entries:
            request = entry.request
            if request.url.startswith("COMMENT"):
                name = request.url.split("/")[-1]
                pages.append(
                    Page(
                        startedDateTime=entry.startedDateTime,
                        id=name,
                        title=name,
                        pageTimings=PageTimings(onContentLoad=-1, onLoad=-1),
                    )
                )
                continue
            pageref = pages[-1].id if len(pages) else entry.pageref
            entry.pageref = pageref
            entries.append(entry)
        har.pages = pages
        har.entries = entries

    return har
