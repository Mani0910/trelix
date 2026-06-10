# Run this script in PowerShell as Administrator on each Windows VM.
# It configures WinRM (5985) and OpenSSH (client + server).

param(
    [string]$ZipSourcePath,
    [switch]$UseLinuxSCP,
    [string]$LinuxHost = "10.211.27.74",
    [string]$LinuxUser = "root",
    [string]$LinuxZipPath = "/home/Fireeye/IMAGE_HX_AGENT_WIN_36.30.37.zip",
    [string]$DownloadDir = "$env:USERPROFILE\Downloads",
    [string]$ExtractDir,
    [switch]$InstallAfterExtract
)

Set-ExecutionPolicy Unrestricted -Scope Process -Force
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force

winrm quickconfig -q
netstat -an | find "5985"

if (-not (Get-NetFirewallRule -Name "WinRM-HTTP-In-TCP" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name "WinRM-HTTP-In-TCP" -DisplayName "WinRM over HTTP" -Enabled True -Profile Any -Action Allow -Direction Inbound -Protocol TCP -LocalPort 5985
}

# Install OpenSSH Client + Server
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start SSH service
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic

# Ensure SSH firewall rule exists
if (!(Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue | Select-Object Name, Enabled)) {
    Write-Output "Firewall Rule 'OpenSSH-Server-In-TCP' does not exist, creating it..."
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
} else {
    Write-Output "Firewall rule 'OpenSSH-Server-In-TCP' already exists."
}

Set-ExecutionPolicy Restricted -Scope LocalMachine -Force

New-Item -Path $DownloadDir -ItemType Directory -Force | Out-Null

$localZipPath = $null

if ($UseLinuxSCP) {
    if (-not (Get-Command scp -ErrorAction SilentlyContinue)) {
        throw "scp command is not available. Install OpenSSH Client first."
    }

    $remoteSource = "{0}@{1}:{2}" -f $LinuxUser, $LinuxHost, $LinuxZipPath
    Write-Output "Copying ZIP from Linux: $remoteSource"
    Write-Output "When prompted, enter Linux password: Mitel5000"
    & scp $remoteSource $DownloadDir

    if ($LASTEXITCODE -ne 0) {
        throw "SCP copy failed from Linux source: $remoteSource"
    }

    $localZipPath = Join-Path $DownloadDir ([System.IO.Path]::GetFileName($LinuxZipPath))
}
elseif (-not [string]::IsNullOrWhiteSpace($ZipSourcePath)) {
    $zipName = [System.IO.Path]::GetFileName($ZipSourcePath)
    if ([string]::IsNullOrWhiteSpace($zipName)) {
        throw "Invalid ZipSourcePath: $ZipSourcePath"
    }

    $localZipPath = Join-Path $DownloadDir $zipName
    Write-Output "Copying package from: $ZipSourcePath"
    Copy-Item -Path $ZipSourcePath -Destination $localZipPath -Force
}

if ($localZipPath -and (Test-Path $localZipPath)) {
    if ([string]::IsNullOrWhiteSpace($ExtractDir)) {
        $extractFolderName = [System.IO.Path]::GetFileNameWithoutExtension($localZipPath)
        $ExtractDir = Join-Path $DownloadDir $extractFolderName
    }

    New-Item -Path $ExtractDir -ItemType Directory -Force | Out-Null
    Write-Output "Extracting package to: $ExtractDir"
    Expand-Archive -Path $localZipPath -DestinationPath $ExtractDir -Force

    $msiFile = Get-ChildItem -Path $ExtractDir -Recurse -File -Filter *.msi -ErrorAction SilentlyContinue |
        Select-Object -First 1

    Write-Output "ZIP copy and extraction complete."
    Write-Output "Local ZIP: $localZipPath"
    Write-Output "Extracted Folder: $ExtractDir"

    if ($msiFile) {
        Write-Output "Installer found: $($msiFile.FullName)"
        if ($InstallAfterExtract) {
            Write-Output "Installing Trellix silently..."
            Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$($msiFile.FullName)`" /qn /norestart" -Wait
            Write-Output "Silent install command completed."
        }
        else {
            Write-Output "Open this MSI to install: $($msiFile.FullName)"
            Start-Process explorer.exe $ExtractDir
        }
    }
    else {
        Write-Output "No MSI found in extracted folder."
    }
}
else {
    Write-Output "No ZIP copy source provided. Skipping copy and extract step."
}

Write-Output "Windows prerequisite setup complete."
