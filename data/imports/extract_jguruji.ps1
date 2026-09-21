# J-Guruji Extraction Script
# Extracts Class 1-5 curriculum data strictly from jguruji.jharkhand.gov.in

param(
    [string]$OutputDir = "$PSScriptRoot/../../data/curriculum"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$wc = New-Object System.Net.WebClient
$wc.Encoding = [System.Text.Encoding]::UTF8

Write-Host "Fetching SummaryResources from J-Guruji..."
$summaryUrl = "https://jguruji.jharkhand.gov.in/Website/SummaryResources?Language=0&Source=0"
$html = $wc.DownloadString($summaryUrl)

# Find all links that have > 0 resources for classes 1-5
# Pattern matches rows: Class (1-5), Subject, Lang, Source, and then td cells with links
$pattern = '(?s)<tr>\s*<td class="text-center">([1-5])</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*(.*?)</tr>'
$rowMatches = [regex]::Matches($html, $pattern)
Write-Host "Found $($rowMatches.Count) Class 1-5 subject/resource summary rows"

$linksToFetch = @()

foreach ($row in $rowMatches) {
    $classNum = [int]$row.Groups[1].Value
    $subjectName = $row.Groups[2].Value.Trim()
    $lang = $row.Groups[3].Value.Trim()
    $source = $row.Groups[4].Value.Trim()
    $tds = $row.Groups[5].Value

    # Find all links with count > 0
    # format: <a href="/Website/SummaryDetails?...">count</a>
    $linkMatches = [regex]::Matches($tds, 'href="([^"]+)">(\d+)</a>')
    foreach ($lm in $linkMatches) {
        $href = [System.Net.WebUtility]::HtmlDecode($lm.Groups[1].Value)
        $count = [int]$lm.Groups[2].Value
        if ($count -gt 0) {
            $fullUrl = "https://jguruji.jharkhand.gov.in$href"
            $linksToFetch += [PSCustomObject]@{
                Class = $classNum
                Subject = $subjectName
                Language = $lang
                Source = $source
                Url = $fullUrl
                Count = $count
            }
        }
    }
}

Write-Host "Found $($linksToFetch.Count) resource endpoints with count > 0 for Class 1-5."

$records = @()
$seenKeys = @{}

$processed = 0
foreach ($item in $linksToFetch) {
    $processed++
    Write-Host "[$processed/$($linksToFetch.Count)] Fetching $($item.Subject) (Class $($item.Class)) from: $($item.Url)..."
    try {
        $detailHtml = $wc.DownloadString($item.Url
        
        
        )

        # Parse table headers to find column indices
        $thMatches = [regex]::Matches($detailHtml, '(?s)<th[^>]*>(.*?)</th>')
        $headers = @()
        foreach ($th in $thMatches) {
            $headers += ($th.Groups[1].Value -replace '<[^>]+>', '').Trim()
        }

        $hasTopic = ($headers -contains "Topic Name")

        # Parse tbody rows
        $tbodyMatch = [regex]::Match($detailHtml, '(?s)<tbody>(.*?)</tbody>')
        if ($tbodyMatch.Success) {
            $rowRegex = [regex]::Matches($tbodyMatch.Groups[1].Value, '(?s)<tr>(.*?)</tr>')
            foreach ($r in $rowRegex) {
                $cells = [regex]::Matches($r.Groups[1].Value, '(?s)<td[^>]*>(.*?)</td>')
                if ($cells.Count -ge 5) {
                    $sNo = ($cells[0].Groups[1].Value -replace '<[^>]+>', '').Trim()
                    $classVal = ($cells[1].Groups[1].Value -replace '<[^>]+>', '').Trim()
                    $subjVal = ($cells[2].Groups[1].Value -replace '<[^>]+>', '').Trim()
                    $subjHindiVal = ($cells[3].Groups[1].Value -replace '<[^>]+>', '').Trim()
                    $chapVal = ($cells[4].Groups[1].Value -replace '<[^>]+>', '').Trim()
                    $chapHindiVal = ""
                    if ($cells.Count -ge 6) {
                        $chapHindiVal = ($cells[5].Groups[1].Value -replace '<[^>]+>', '').Trim()
                    }
                    $topicVal = ""
                    if ($cells.Count -ge 7) {
                        $topicVal = ($cells[6].Groups[1].Value -replace '<[^>]+>', '').Trim()
                    }

                    if ($classVal -and $subjVal -and ($chapVal -or $chapHindiVal)) {
                        $uniqueKey = "$classVal|$subjVal|$chapVal|$chapHindiVal|$topicVal"
                        if (-not $seenKeys.ContainsKey($uniqueKey)) {
                            $seenKeys[$uniqueKey] = $true
                            $records += [PSCustomObject]@{
                                class_number = [int]$classVal
                                subject = $subjVal
                                subject_hindi = $subjHindiVal
                                chapter = $chapVal
                                chapter_hindi = $chapHindiVal
                                topic = $topicVal
                                source_url = $item.Url
                                source_name = "J-Guruji Jharkhand"
                                source_authority = "DoSE&L, Govt. of Jharkhand"
                            }
                        }
                    }
                }
            }
        }
    } catch {
        Write-Warning "Failed to fetch $($item.Url): $_"
    }
}

Write-Host "Extraction completed! Total unique syllabus items extracted: $($records.Count)"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$outPath = Join-Path $OutputDir "jguruji_class1_5_raw.json"
$recordsJson = $records | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($outPath, $recordsJson, [System.Text.Encoding]::UTF8)

Write-Host "Saved extracted curriculum to $outPath"

# Summary counts
$summary = $records | Group-Object class_number | Select-Object Name, Count
Write-Host "Summary by Class:"
$summary | Format-Table -AutoSize
