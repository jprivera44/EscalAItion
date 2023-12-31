# Escalation Risks from Language Models in Military and Diplomatic Decision-Making


Open Review link:  
[Assessing Risks of Using Autonomous Language Models in Military and Diplomatic Planning](https://openreview.net/forum?id=5HuBX8LvuT)



## Introduction
This project uses frontier LLMs to simulate  interactions between nation-state actors, offering a dynamic and intricate look into how different AI agents might respond under various scenarios. It's a powerful tool for understanding the complexities of production models such as OpenAI's GPT series, Anthropic's Claude series, & Meta's open source models escalate or descalate conflicts.

## Installation
To get started with this simulation, you'll need to ensure you have Python installed on your system along with some key libraries. Follow these steps:

0. Clone the Repository:

```
git clone https://github.com/jprivera44/EscalAItion.git
```

1. Create a python environment

```
conda create -n escalaition python=3.11
conda activate escalaition
```

2. Install Pytorch separately
> https://pytorch.org/get-started/locally/

3. Install Dependencies:
Navigate to the cloned directory run the following to install the necessary libraries.

```
pip install -r requirements.txt 
```

## Usage

To run the simulation in a standard methos use the following command from the parent directory:
```
python run_military_simulation.py
```

To run the simulation with mock nations, wihtout calling any APIs LLMs

```
python run_military_simulation.py --nation_model mock --world_model mock
```


## Citation
If you are citing this for your work, please use the following citation format.

```
@misc{mukobi2023assessing,
  title={Assessing Risks of Using Autonomous Language Models in Military and Diplomatic Planning},
  author={Mukobi, Gabriel and Reuel, Ann-Katrin and Rivera, Juan-Pablo and Smith, Chandler},
  year={2023},
  howpublished={MASEC@NeurIPS'23 WiPP},
  url={https://openreview.net/forum?id=5HuBX8LvuT}
}

```


## Contributing
We welcome contributions to this project! If you have ideas for improvements or have found a bug, please feel free to open an issue or submit a pull request.


## License
This project is licensed under the MIT License. For more details, see the LICENSE file in the repository.
