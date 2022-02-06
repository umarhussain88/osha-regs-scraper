CREATE TABLE [stg2].[oshaLOIjson]
(
  id     bigint PRIMARY KEY IDENTITY,
  batchKey bigint,
  jsonBody     nvarchar(max)
);

ALTER TABLE  [stg2].[oshaLOIjson]
  ADD CONSTRAINT [jsonBody record should be formatted as JSON]
    CHECK (ISJSON(jsonBody) = 1)

;