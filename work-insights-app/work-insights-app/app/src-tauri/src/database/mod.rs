pub mod schema;
pub mod queries;

use rusqlite::{Connection, Result};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

pub type DbConnection = Arc<Mutex<Connection>>;

pub fn initialize_database(db_path: PathBuf) -> Result<DbConnection> {
    let conn = Connection::open(db_path)?;
    schema::create_tables(&conn)?;
    Ok(Arc::new(Mutex::new(conn)))
}
