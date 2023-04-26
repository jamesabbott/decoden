import typer
import os
import json
from os.path import join
from pathlib import Path
from typing import Optional, List

from decoden.pipeline import _decoden_pipeline


from decoden.preprocessing.pipeline import run_preprocessing
from decoden.utils import print_message, extract_conditions
from decoden.denoising.nmf import run_NMF
from decoden.denoising.hsr import run_HSR, run_HSR_replicates

# from decoden.apps.denoise_app import denoise_app
from decoden.apps.run_app import run_app

app = typer.Typer()
denoise_app = typer.Typer()



app.add_typer(denoise_app, name="denoise")
app.add_typer(run_app, name="run")

@app.callback()
def callback():
    """
    Multi-condition ChIP-Seq Analysis with DecoDen
    """
    print_message()
    

@app.command("preprocess")
def preprocess(
    input_csv: Optional[Path] = typer.Option(None, "--input_csv", "-i", help="""Path to CSV file with information about 
                                            experimental conditions. Must contain `filepath`, `exp_name` and `is_control` columns. 
                                            Control/input should be the first condition. Input files can be in BED/BAM format."""), 
    bin_size: int = typer.Option(200, "--bin_size", "-bs", help="""Aize of genomic bin for tiling. 
                                Recommended value is 10-200. Smaller bin size increases space and runtime, larger binsizes may occlude small variations. 
                                """), 
    num_jobs: int = typer.Option(1, "--num_jobs", "-n", help="Number of parallel jobs for preprocessing."), 
    out_dir: Optional[Path] = typer.Option(None, "--out_dir", "-o", help="Path to directory where all output files will be written"), 
    ):
    """
    Preprocess data to be in the correct format for DecoDen
    """

    
    typer.echo("Preprocessing data")
    
    _decoden_pipeline(["preprocess"], input_csv=input_csv, bin_size=bin_size, num_jobs=num_jobs, out_dir=out_dir)





@denoise_app.command("consolidate")
def denoise_consolidated(
    # data_folder:  Optional[Path] = typer.Option(None, "--data_folder", "-df", help="Path to preprocessed data files in BED format"), 
    files_reference: Optional[Path] = typer.Option(None, "--files_reference", "-f", help="""Path to JSON file with experiment conditions. 
                        If you used DecoDen for pre-processing, use the `experiment_conditions.json` file"""), 
    control_label: str  = typer.Option("control", "--control_condition", "-con", help="The label for the control/input samples."), 
    
    # conditions: List[str] = typer.Option(None, "--conditions", "-c", help="List of experimental conditions. First condition MUST correspond to the control/input samples."), 
    out_dir: Optional[Path] = typer.Option(None, "--out_dir", "-o", help="Path to directory where all output files will be written"), 
    blacklist_file: Optional[Path] = typer.Option(None, "--blacklist_file", "-bl", help="Path to blacklist file. Make sure to use the blacklist that is appropriate for the genome assembly/organism."), 
    alpha_W: float  = typer.Option(0.01, "--alpha_W", "-aW", help="Regularisation for the signal matrix."), 
    alpha_H: float  = typer.Option(0.001, "--alpha_H", "-aH", help="Regularisation for the mixing matrix."), 
    control_cov_threshold: float  = typer.Option(0.1, "--control_cov_threshold", "-cov", help="""Threshold for coverage in control samples. Only genomic bins above this threshold will be used. 
                                It is recommended to choose a value larger than 1/bin_size."""), 
    n_train_bins: int  = typer.Option(50000, "--n_train_bins", "-nt", help="Number of genomic bins to be used for training."), 
    chunk_size: int  = typer.Option(50000, "--chunk_size", "-ch", help="Chunk size for processing the signal matrix. Should be smaller than `n_train_bins`."), 
    seed: int  = typer.Option(0, "--seed", "-s", help="Random state."), 
    plotting: bool  = typer.Option(False, "--plotting", "-p", help="Plot sanity checks for extracted matrices."), 
):
    """
    Run decoden to denoise and pool your data
    """

    _decoden_pipeline(["nmf", "hsr_consolidate"], 
                      files_reference=files_reference, 
                      control_label=control_label, 
                      out_dir=out_dir, 
                      blacklist_file=blacklist_file,
                      alpha_W=alpha_W,
                      alpha_H=alpha_H,
                      control_cov_threshold=control_cov_threshold,
                      n_train_bins=n_train_bins,
                      chunk_size=chunk_size,
                      seed=seed,
                      plotting=plotting                      
                      )
    
    typer.echo("\nDecoDen complete!")
    
    
    

@app.command()
def detect():
    """
    Detect peaks
    """
    typer.echo("Detecting peaks")

