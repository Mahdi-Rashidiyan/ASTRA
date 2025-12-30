# ASTRA








# ASTRA: HPC Shell Physics-Oriented

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-55.9%25-blue)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-40.3%25-orange)
![Shell](https://img.shields.io/badge/shell-3.8%25-green)

> **ASTRA** is a high-performance computing (HPC) shell with physics-oriented features, designed to facilitate efficient job management and resource monitoring in computational physics environments.

## 🚀 Features

-   **HPC Job Management**: Streamlined submission and monitoring of computational jobs
-   **Resource Monitoring**: Real-time tracking of CPU, memory, and disk usage
-   **Physics-Oriented Tools**: Specialized utilities for physics simulations and calculations
-   **Shell Interface**: Command-line interface for efficient interaction with HPC systems
-   **Queue Management**: Advanced job queuing and scheduling capabilities
-   **Logging System**: Comprehensive logging for debugging and audit trails

## 📁 Project Structure

```
ASTRA/
├── HPC_Job_Management.ipynb    # Jupyter notebook for job management
├── LICENSE                     # MIT license file
├── README.md                   # This file
├── builtin.py                  # Built-in commands and functions
├── config.py                   # Configuration management
├── cpu.py                      # CPU monitoring and management
├── disk.py                     # Disk operations and monitoring
├── executor.py                 # Job execution engine
├── hpc_advanced_features.py    # Advanced HPC functionalities
├── logger.py                   # Logging system
├── main.py                     # Main application entry point
├── parser.py                   # Command parser
├── queue.py                    # Job queue management
├── resource.py                 # Resource allocation and monitoring
├── setup.sh                    # Setup script
└── shell.py                    # Shell interface implementation
```

## 🛠️ Installation

### Prerequisites

- Python 3.6 or higher
- Jupyter Notebook
- Linux/Unix environment (recommended for HPC systems)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/Mahdi-Rashidiyan/ASTRA.git
cd ASTRA
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Install required Python packages:
```bash
pip install -r requirements.txt
```

> **Note**: If `requirements.txt` is not present, install the dependencies manually based on the import statements in the source files.

## 📖 Usage

### Basic Shell Interface

Launch the ASTRA shell:
```bash
python main.py
```

### Job Management with Jupyter

Open the HPC job management notebook:
```bash
jupyter notebook HPC_Job_Management.ipynb
```

### Key Commands

| Command | Description |
|---------|-------------|
| `submit` | Submit a new job to the queue |
| `monitor` | Monitor resource usage |
| `queue` | View job queue status |
| `cancel` | Cancel a running job |
| `logs` | View job logs |

## 🔧 Configuration

Configure ASTRA by editing the `config.py` file:

```python
# Example configuration settings
HPC_SETTINGS = {
    'max_jobs': 100,
    'default_priority': 'normal',
    'log_level': 'INFO',
    'resource_limits': {
        'max_memory': '64GB',
        'max_cpu_time': 24  # hours
    }
}
```

## 📊 Monitoring Capabilities

ASTRA provides comprehensive monitoring of:

- **CPU Usage**: Real-time CPU utilization and core allocation
- **Memory Usage**: RAM consumption and allocation patterns
- **Disk I/O**: Read/write operations and storage availability
- **Job Status**: Queue position, runtime, and completion status

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. Follow PEP 8 Python style guidelines
2. Add appropriate logging for new features
3. Update documentation for new functionalities
4. Test thoroughly in HPC environments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details【turn0fetch0】.

## 🙏 Acknowledgments

- The computational physics community for inspiration and requirements
- HPC centers for providing testing environments
- Open-source contributors who have made this project possible

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the `HPC_Job_Management.ipynb` notebook for examples
- Review the logging output for debugging information

---

**ASTRA** - Bridging the gap between high-performance computing and physics simulations with an intuitive shell interface.
