# Notebook-generated report assets

Export every data-derived report figure and results table from your AIP304 Jupyter notebook into this directory. Keep the corresponding export code in the submitted notebook, along with the fixed data manifest, seeds and environment details needed to reproduce it.

For example, save a figure as `generated/confusion-matrix.png` and include it from either language file:

```tex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.92\linewidth]{confusion-matrix.png}
  \caption{Replace this with the evaluated split, class labels, colour scale and sample count.}
  \label{fig:confusion}
\end{figure}
```

Export a table body to `generated/results.tex` and use `\input{generated/results.tex}` inside a numbered `table` environment. The workflow compiles these committed assets; it does not train models or regenerate results. A figure placeholder in the starter template is not experimental evidence.

PDF figures are tracked normally in this standalone project; generated build output under build/ and dist/ is ignored. Do not add PlantSeg images, private data, or large checkpoints solely to make this report build.
