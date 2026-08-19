use std::fs;

use tauri::Manager;
use tauri_plugin_shell::ShellExt;


#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let data_dir = app
                .path()
                .app_local_data_dir()?;

            fs::create_dir_all(&data_dir)?;

            let argumentos = vec![
                "--data-dir".to_string(),
                data_dir.to_string_lossy().to_string(),
                "--parent-pid".to_string(),
                std::process::id().to_string(),
                "--port".to_string(),
                "8765".to_string(),
            ];

            let (_eventos, _processo) = app
                .shell()
                .sidecar("lumina-api")?
                .args(argumentos)
                .spawn()?;

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("não foi possível iniciar o Skin Admin");
}
