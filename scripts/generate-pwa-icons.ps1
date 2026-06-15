Add-Type -AssemblyName System.Drawing

$outDir = Join-Path $PSScriptRoot "..\images\icons"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$navyStart = [System.Drawing.ColorTranslator]::FromHtml("#1a1a2e")
$navyEnd   = [System.Drawing.ColorTranslator]::FromHtml("#0f3460")
$coral     = [System.Drawing.ColorTranslator]::FromHtml("#ff6b6b")
$teal      = [System.Drawing.ColorTranslator]::FromHtml("#4ecdc4")

function New-KinkIcon {
    param(
        [int]$Size,
        [string]$Path,
        [double]$CornerRatio = 0.18
    )

    $bmp = New-Object System.Drawing.Bitmap($Size, $Size, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb))
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

    $rect = New-Object System.Drawing.Rectangle(0, 0, $Size, $Size)

    # Background: diagonal navy gradient, matches the site body background
    $bgBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, $navyStart, $navyEnd, 45.0)

    $radius = [double]$Size * $CornerRatio
    $bgPath = New-Object System.Drawing.Drawing2D.GraphicsPath
    if ($radius -gt 0) {
        $d = $radius * 2
        $bgPath.AddArc(0, 0, $d, $d, 180, 90)
        $bgPath.AddArc($Size - $d, 0, $d, $d, 270, 90)
        $bgPath.AddArc($Size - $d, $Size - $d, $d, $d, 0, 90)
        $bgPath.AddArc(0, $Size - $d, $d, $d, 90, 90)
        $bgPath.CloseFigure()
    } else {
        $bgPath.AddRectangle($rect)
    }
    $g.FillPath($bgBrush, $bgPath)

    # "K" wordmark with coral -> teal gradient (matches glitch-mini logo colors)
    $fontSize = [single]([double]$Size * 0.6)
    $fontFamily = New-Object System.Drawing.FontFamily("Segoe UI")
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center

    $layout = New-Object System.Drawing.RectangleF(0, 0, $Size, $Size)
    $textPath = New-Object System.Drawing.Drawing2D.GraphicsPath
    $textPath.AddString("K", $fontFamily, [int][System.Drawing.FontStyle]::Bold, $fontSize, $layout, $sf)

    $bounds = $textPath.GetBounds()
    $offsetX = (([double]$Size - $bounds.Width) / 2.0) - $bounds.X
    $offsetY = (([double]$Size - $bounds.Height) / 2.0) - $bounds.Y
    $m = New-Object System.Drawing.Drawing2D.Matrix
    $m.Translate($offsetX, $offsetY)
    $textPath.Transform($m)

    $textBounds = $textPath.GetBounds()
    $textRect = New-Object System.Drawing.RectangleF($textBounds.X, $textBounds.Y, $textBounds.Width, $textBounds.Height)
    $textBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush($textRect, $coral, $teal, 45.0)
    $g.FillPath($textBrush, $textPath)

    $bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)

    $g.Dispose()
    $bmp.Dispose()
    $bgPath.Dispose()
    $textPath.Dispose()
}

# Maskable/any icons (full square, content fits within the safe-zone circle)
New-KinkIcon -Size 512 -Path (Join-Path $outDir "icon-512.png")
New-KinkIcon -Size 192 -Path (Join-Path $outDir "icon-192.png")

# Apple touch icon - iOS adds its own rounding, so a smaller corner radius works best
New-KinkIcon -Size 180 -Path (Join-Path $outDir "icon-180.png") -CornerRatio 0.0

# Favicons
New-KinkIcon -Size 32 -Path (Join-Path $outDir "icon-32.png")
New-KinkIcon -Size 16 -Path (Join-Path $outDir "icon-16.png")

Write-Output "Icons generated in $outDir"
