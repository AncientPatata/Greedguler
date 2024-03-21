use std::{
    collections::HashMap,
    fs::File,
    io::{BufReader, Read},
};

use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::Deserialize;
use serde_json::Value;
use simd_json;

use dict_derive::{FromPyObject, IntoPyObject};

#[derive(Deserialize, FromPyObject, IntoPyObject)]
#[pyclass(extends=PyDict)]
struct ParsedData {
    nodes: HashMap<String, ParsedNodeData>,
}

#[derive(Deserialize, FromPyObject, IntoPyObject)]
struct ParsedNodeData {
    #[serde(rename = "Data")]
    data: String,
    #[serde(rename = "Dependencies")]
    dependencies: Vec<u32>,
}

/// Formats the sum of two numbers as string.
#[pyfunction]
fn parse_json_graph(filename: String) -> PyResult<ParsedData> {
    // Open the file for efficient, buffered reading
    let file = File::open(filename)?;
    let mut reader = BufReader::new(file);

    // // Read the file directly into a Vec<u8>
    // let mut json_bytes = Vec::new();
    // reader.read_to_end(&mut json_bytes)?;

    let v: ParsedData = simd_json::serde::from_reader(&mut reader).unwrap();

    Ok(v)
}

/// A Python module implemented in Rust.
#[pymodule]
fn rapid_scheduler(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_json_graph, m)?)?;

    Ok(())
}
