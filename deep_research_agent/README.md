## Deep Research Agent From Scratch

This is part of the "Building Agents from scratch" series that will be potentially moved to it's own separate project. We will build a Deep Research Agent from scratch without using any LLM orchestration frameworks. We will also learn about nuances of DeepSeek-R1 family of reasoning models.

### The topology of the system we will be building is as follows:

<p align="center">
<img src="../../assets/dra_topology_0.png" width="50%" alt="Deep Research Agent">
</p>

1. A user will provide a query or topic to be researched.

2. A LLM will create an outline of the final report that it will be aiming for. It will be instructed to produce not more than a certain number of paragraphs.

3. Each of the paragraph description will be fed into a research process separately to produce a comprehensive set of information to be used in report construction. Detailed description of the research process will be outlined in the next section.

4. All of the information will be fed into summarisation step that will construct the final report including conclusion.

5. The report will then be delivered to the user in MarkDown form.

### Zoom in into each of the research steps:

<p align="center">
<img src="../../assets/dra_topology_1.png" width="50%" alt="Deep Research Agent, Research Step">
</p>

1. Once we have the outline of each paragraph, it will be passed to a LLM to construct Web Search queries in an attempt to best enrich the information needed.

2. The LLM will output the search query and the reasoning behind it.

3. We will execute Web search against the query and retrieve top relevant results.

4. The results will be passed to the Reflection step where a LLM will reason about any missed nuances to try and come up with a search query that would enrich the initial results.

5. This process will be repeated for n times in an attempt to get the best set of information possible.

You can find the detailed walkthrough of this project in my [Newsletter](https://www.newsletter.swirlai.com/p/building-deep-research-agent-from).


## Running the code

[uv](https://github.com/astral-sh/uv) is a great tool for Python dependency management. To run the code:

- Copy the `env.example` file to `.env` and set the correct values:

```bash
cp env.example .env
```
- Get your credentials for SambaNova API [here](https://fnf.dev/4aVUqro) and Tavily API [here](https://app.tavily.com/) and save them in the .env file under keys `SAMBANOVA_API_KEY` and `TAVILY_API_KEY` respectively.

- We can now run the project:

```bash
uv run --env-file .env src/topology.py --topic "Topic to be researched"
```
    For example:

```bash
uv run --env-file .env src/topology.py --topic "Something interesting about humans"
```
It will take some time to execute (~5 minutes) and you will get your research report in Markdown format in the `reports` folder.

## Interactive Notebook

For a more interactive learning experience, you can follow along with the Jupyter notebook in the [notebooks](notebooks) folder. While detailed documentation is still being worked on, you can find the complete implementation and follow the code there.