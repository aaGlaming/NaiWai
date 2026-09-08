param(
    [string]$ChromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
)

$desktopDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $desktopDir
$renderPath = Join-Path $desktopDir "icon-render.html"
$pngPath = Join-Path $desktopDir "naiwa-icon.png"
$icoPath = Join-Path $desktopDir "naiwa.ico"
$renderUri = ([Uri]$renderPath).AbsoluteUri

& $ChromePath --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=256,256 `
    --default-background-color=00000000 --screenshot=$pngPath $renderUri
if (-not (Test-Path -LiteralPath $pngPath)) {
    throw "Failed to render the application icon"
}

$png = [IO.File]::ReadAllBytes($pngPath)
$stream = [IO.MemoryStream]::new()
$writer = [IO.BinaryWriter]::new($stream)
$writer.Write([UInt16]0)
$writer.Write([UInt16]1)
$writer.Write([UInt16]1)
$writer.Write([Byte]0)
$writer.Write([Byte]0)
$writer.Write([Byte]0)
$writer.Write([Byte]0)
$writer.Write([UInt16]1)
$writer.Write([UInt16]32)
$writer.Write([UInt32]$png.Length)
$writer.Write([UInt32]22)
$writer.Write($png)
$writer.Flush()
[IO.File]::WriteAllBytes($icoPath, $stream.ToArray())
$writer.Dispose()
$stream.Dispose()
Write-Output $icoPath
