; Coddy V3 Installer Script for NSIS
; To use:
; 1. Install NSIS: https://nsis.sourceforge.io/Download
; 2. Ensure your CoddyV3.exe is in the 'dist' folder.
; 3. Right-click this file and "Compile NSIS Script".

!define APP_NAME "Coddy V3"
!define EXE_NAME "CoddyV3.exe"
!define COMPANY_NAME "Coddy"
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

; Global variable to hold the uninstaller checkbox state
Var /GLOBAL UNINSTALL_SETTINGS

;--------------------------------
; General Installer Settings

Name "${APP_NAME} ${APP_VERSION}"
OutFile "dist\CoddyV3_Installer.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "${UNINSTALL_KEY}" "InstallLocation"
RequestExecutionLevel admin ; Request admin privileges for the installer

;--------------------------------
; Modern UI Interface Settings

!include "MUI2.nsh"
!if /fileexists "assets\icon.ico"
    !define MUI_ICON "assets\icon.ico"
    !define MUI_UNICON "assets\icon.ico"
!endif

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
 
; --- Uninstaller Pages ---
; Custom function to read the checkbox state when leaving the confirm page
Function un.ConfirmPageLeave
  ; The MUI_UNGET_CHECKBOX_STATE macro is not available at compile time here.
  ; We use the underlying commands to get the checkbox state.
  ; The control ID for the checkbox on the un.Confirm page is 1203.
  FindWindow $R0 "#32" "" $HWNDPARENT
  GetDlgItem $R1 $R0 1203
  SendMessage $R1 ${BM_GETSTATE} 0 0 $UNINSTALL_SETTINGS
FunctionEnd
 
!define MUI_UNCONFIRMPAGE_TEXT_TOP "This will remove Coddy V3 from your computer. Your projects in the Documents folder will not be removed."
!define MUI_UNCONFIRMPAGE_CHECKBOX "Also remove all personal settings and logs from AppData?"
!define MUI_UNCONFIRMPAGE_CHECKBOX_STATE 0
!define MUI_UNPAGE_CUSTOMFUNCTION_LEAVE un.ConfirmPageLeave
!insertmacro MUI_UNPAGE_CONFIRM
!undef MUI_UNPAGE_CUSTOMFUNCTION_LEAVE
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Section

Section "Install"
  SetOutPath $INSTDIR

  ; Copy the main executable from your build directory
  File "dist\${EXE_NAME}"
  
  ; Copy the license and the generated changelog
  File "LICENSE"
  File "dist\changelog.md"

  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\${COMPANY_NAME}"
  CreateShortCut "$SMPROGRAMS\${COMPANY_NAME}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"

  ; Write uninstaller information to the registry
  WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "${UNINSTALL_KEY}" "Publisher" "${COMPANY_NAME}"
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"
  ; Check if the user wants to remove personal data
  ${If} $UNINSTALL_SETTINGS == ${BST_CHECKED}
    ; User wants to remove AppData. The path is %APPDATA%\Coddy
    RMDir /r "$APPDATA\Coddy"
  ${EndIf}

  ; It's safer to delete files before trying to remove directories
  Delete "$INSTDIR\${EXE_NAME}"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\changelog.md"
  Delete "$INSTDIR\uninstall.exe"

  ; Remove shortcuts
  Delete "$SMPROGRAMS\${COMPANY_NAME}\${APP_NAME}.lnk"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  
  ; Remove directories if empty
  RMDir "$SMPROGRAMS\${COMPANY_NAME}"
  RMDir "$INSTDIR"

  ; Remove registry keys
  DeleteRegKey HKLM "${UNINSTALL_KEY}"
SectionEnd