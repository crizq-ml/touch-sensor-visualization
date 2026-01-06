Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# --- SETUP MAIN FORM ---
[System.Windows.Forms.Application]::EnableVisualStyles()
$form = New-Object System.Windows.Forms.Form
$form.Text = "Stream Controller"
$form.Size = New-Object System.Drawing.Size(320, 440)
$form.StartPosition = "CenterScreen"
$form.BackColor = "White"
$form.FormBorderStyle = "FixedSingle"
$form.MaximizeBox = $false

# --- PROCESS LOGIC ---
$scriptPath = $PSScriptRoot
if (-not $scriptPath) { $scriptPath = Get-Location }
$global:StreamProcess = $null
$global:GuiProcess = $null

function Start-MyProcess {
    param([string]$Name, [string]$Command)
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo.FileName = "powershell.exe"
    $p.StartInfo.Arguments = "-WindowStyle Hidden -Command `"$Command`"" 
    $p.StartInfo.WorkingDirectory = $scriptPath
    $p.Start() | Out-Null
    return $p
}

function Stop-MyProcess {
    param([System.Diagnostics.Process]$Proc)
    if ($Proc -ne $null -and -not $Proc.HasExited) {
        Stop-Process -Id $Proc.Id -Force -ErrorAction SilentlyContinue
    }
}

# --- STATUS LABELS SECTION ---
$lblStreamStatus = New-Object System.Windows.Forms.Label
$lblStreamStatus.Text = "Stream: STOPPED"
$lblStreamStatus.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$lblStreamStatus.ForeColor = "#ff746c" # Red
$lblStreamStatus.AutoSize = $false
$lblStreamStatus.TextAlign = "MiddleCenter"
$lblStreamStatus.Size = New-Object System.Drawing.Size(300, 30)
$lblStreamStatus.Location = New-Object System.Drawing.Point(10, 10)
$form.Controls.Add($lblStreamStatus)

$lblGuiStatus = New-Object System.Windows.Forms.Label
$lblGuiStatus.Text = "GUI App: STOPPED"
$lblGuiStatus.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$lblGuiStatus.ForeColor = "#ff746c" # Red
$lblGuiStatus.AutoSize = $false
$lblGuiStatus.TextAlign = "MiddleCenter"
$lblGuiStatus.Size = New-Object System.Drawing.Size(300, 30)
$lblGuiStatus.Location = New-Object System.Drawing.Point(10, 40)
$form.Controls.Add($lblGuiStatus)

$lblHeaderDiv = New-Object System.Windows.Forms.Label
$lblHeaderDiv.Text = "______________________________"
$lblHeaderDiv.ForeColor = "#eeeeee"
$lblHeaderDiv.AutoSize = $true
$lblHeaderDiv.Location = New-Object System.Drawing.Point(40, 60)
$form.Controls.Add($lblHeaderDiv)


# --- ROUNDED BUTTON FUNCTION ---
function New-RoundedButton {
    param([string]$Text, [string]$ColorHex, [int]$Top, [scriptblock]$OnClick)

    $realColor = [System.Drawing.ColorTranslator]::FromHtml($ColorHex)
    $btn = New-Object System.Windows.Forms.Button
    $btn.Text = $Text
    $btn.Location = New-Object System.Drawing.Point(40, $Top)
    $btn.Size = New-Object System.Drawing.Size(220, 45)
    
    $btn.BackColor = $realColor
    $btn.FlatStyle = "Flat"
    $btn.FlatAppearance.BorderSize = 0
    $btn.ForeColor = "White"
    $btn.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
    $btn.Cursor = [System.Windows.Forms.Cursors]::Hand
    $btn.UseVisualStyleBackColor = $false 

    $paintScript = {
        param($sender, $e)
        $g = $e.Graphics
        $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
        $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

        $rect = $sender.ClientRectangle; $rect.Width -= 1; $rect.Height -= 1
        $radius = 20
        $path = New-Object System.Drawing.Drawing2D.GraphicsPath
        $path.AddArc($rect.X, $rect.Y, $radius, $radius, 180, 90)
        $path.AddArc($rect.Right - $radius, $rect.Y, $radius, $radius, 270, 90)
        $path.AddArc($rect.Right - $radius, $rect.Bottom - $radius, $radius, $radius, 0, 90)
        $path.AddArc($rect.X, $rect.Bottom - $radius, $radius, $radius, 90, 90)
        $path.CloseFigure()
        
        $sender.Region = New-Object System.Drawing.Region($path)
        $brush = New-Object System.Drawing.SolidBrush($realColor)
        $g.FillPath($brush, $path)
        
        $stringFormat = New-Object System.Drawing.StringFormat
        $stringFormat.Alignment = "Center"
        $stringFormat.LineAlignment = "Center"
        [System.Drawing.RectangleF]$rectF = $rect
        $g.DrawString($sender.Text, $sender.Font, [System.Drawing.Brushes]::White, $rectF, $stringFormat)
    }
    $btn.Add_Paint($paintScript.GetNewClosure())
    $btn.Add_Click($OnClick)
    return $btn
}

# --- ADD BUTTONS ---

# 1. Start Stream
$form.Controls.Add((New-RoundedButton -Text "Start Stream" -ColorHex "#84e793" -Top 90 -OnClick {
    
    # --- [EDIT HERE] STREAM COMMAND ---
    $cmd = "Write-Host 'Streaming...'; Start-Sleep -Seconds 1000"
    
    $global:StreamProcess = Start-MyProcess -Name "Stream" -Command $cmd
    $lblStreamStatus.Text = "Stream: RUNNING"
    $lblStreamStatus.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#84e793") 
}))

# 2. Stop Stream
$form.Controls.Add((New-RoundedButton -Text "Stop Stream" -ColorHex "#ff746c" -Top 145 -OnClick {
    Stop-MyProcess -Proc $global:StreamProcess
    $lblStreamStatus.Text = "Stream: STOPPED"
    $lblStreamStatus.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#ff746c")
}))

# Divider
$lblDiv = New-Object System.Windows.Forms.Label
$lblDiv.Text = "______________________________"
$lblDiv.ForeColor = "#cccccc"
$lblDiv.AutoSize = $true
$lblDiv.Location = New-Object System.Drawing.Point(40, 200)
$form.Controls.Add($lblDiv)

# 3. Start GUI
$form.Controls.Add((New-RoundedButton -Text "Start GUI" -ColorHex "#59b6f3" -Top 230 -OnClick {
    
    # --- [EDIT HERE] GUI COMMAND ---
    $cmd = "Write-Host 'GUI Running...'; Start-Sleep -Seconds 1000"
    
    $global:GuiProcess = Start-MyProcess -Name "GUI" -Command $cmd
    $lblGuiStatus.Text = "GUI App: RUNNING"
    $lblGuiStatus.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#59b6f3")
}))

# 4. Stop GUI
$form.Controls.Add((New-RoundedButton -Text "Stop GUI" -ColorHex "#ff746c" -Top 285 -OnClick {
    Stop-MyProcess -Proc $global:GuiProcess
    $lblGuiStatus.Text = "GUI App: STOPPED"
    $lblGuiStatus.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#ff746c")
}))

$form.Add_Load({ $form.Refresh() })
$form.ShowDialog() | Out-Null