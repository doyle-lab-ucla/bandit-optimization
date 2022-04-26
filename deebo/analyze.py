import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def calculate_baseline(chemarms: list):
    # TODO: take chem arms, calculate a baseline for probability in a traditional reaction optimziation way
    from chem_arms import ChemArm

    # type check; check chem arms are from same dataset
    url = chemarms[0].data_url
    name = chemarms[0].name
    for arm in chemarms:
        assert isinstance(arm, ChemArm), "required argument: a list of ChemArm objects"
        assert arm.name == name, "ChemArm objects should describe same reaction components"
        assert arm.data_url == url, "ChemArm objects should come from the same dataset"

    df = pd.read_csv(url)

    temp = df[list(name)]

    return


def plot_probs_choosing_best_arm(fn_list,
                                 legend_list,
                                 baseline=0,
                                 best_arm_index=0,
                                 fp='',
                                 title='',
                                 legend_title=''):

    assert len(fn_list) == len(legend_list)

    fps = [fp + fn for fn in fn_list]

    plt.rcParams['savefig.dpi'] = 300
    fig, ax = plt.subplots()

    if baseline != 0:
        plt.axhline(y=baseline, xmin=0, xmax=1, linestyle='dashed', color='black', label='baseline', alpha=0.5)

    for i in range(len(fps)):
        fp = fps[i]
        df = pd.read_csv(fp)
        df = df[['num_sims', 'horizon', 'chosen_arm']]

        n_simulations = int(np.max(df['num_sims'])) + 1
        time_horizon = int(np.max(df['horizon'])) + 1
        all_arms = np.zeros((n_simulations, time_horizon))

        for ii in range(int(n_simulations)):
            all_arms[ii, :] = list(df.loc[df['num_sims'] == ii]['chosen_arm'])

        counts = np.count_nonzero(all_arms == best_arm_index, axis=0)  # average across simulations. shape: (1, time_horizon)
        probs = counts / n_simulations
        ax.plot(np.arange(time_horizon), probs, label=str(legend_list[i]))

    ax.set_xlabel('time horizon')
    ax.set_ylabel('probability of finding best arm')
    ax.set_title(title)
    ax.grid(visible=True, which='both', alpha=0.5)
    ax.legend(title=legend_title)

    plt.show()


def plot_average_reward(fn_list,
                        legend_list,
                        fp='',
                        title='',
                        legend_title=''):

    assert len(fn_list) == len(legend_list)

    fps = [fp + fn for fn in fn_list]

    plt.rcParams['savefig.dpi'] = 300
    fig, ax = plt.subplots()

    for i in range(len(fps)):
        fp = fps[i]
        df = pd.read_csv(fp)
        df = df[['num_sims', 'horizon', 'reward']]

        n_simulations = int(np.max(df['num_sims']))+1
        time_horizon = int(np.max(df['horizon']))+1
        all_rewards = np.zeros((n_simulations, time_horizon))

        for ii in range(int(n_simulations)):
            all_rewards[ii, :] = list(df.loc[df['num_sims'] == ii]['reward'])

        avg_reward = np.average(all_rewards, axis=0)  # average across simulations. shape: (1, time_horizon)
        ax.plot(np.arange(time_horizon), avg_reward, label=str(legend_list[i]))

    ax.set_xlabel('time horizon')
    ax.set_ylabel('average reward')
    ax.set_title(title)
    ax.grid(visible=True, which='both', alpha=0.5)
    ax.legend(title=legend_title, loc='lower right')

    plt.show()


def plot_cumulative_reward(fn_list,
                           legend_list,
                           fp='',
                           title='',
                           legend_title=''):

    assert len(fn_list) == len(legend_list)

    fps = [fp + fn for fn in fn_list]

    plt.rcParams['savefig.dpi'] = 300
    fig, ax = plt.subplots()

    for i in range(len(fps)):
        fp = fps[i]
        df = pd.read_csv(fp)
        df = df[['num_sims', 'horizon', 'cumulative_reward']]

        def get_rewards(df):  # for one simulation, calculate reward (average or cumulative) at each time horizon t
            rewards = df['cumulative_reward'].to_numpy()
            return rewards

        n_simulations = int(np.max(df['num_sims']))+1
        time_horizon = int(np.max(df['horizon']))+1
        all_rewards = np.zeros((n_simulations, time_horizon))

        for ii in range(int(n_simulations)):
            rewards = df.loc[df['num_sims'] == ii]['cumulative_reward'].to_numpy()
            all_rewards[ii, :] = rewards

        probs = np.average(all_rewards, axis=0)  # average across simulations. shape: (1, time_horizon)
        ax.plot(np.arange(time_horizon), probs, label=str(legend_list[i]))

    ax.set_xlabel('time horizon')
    ax.set_ylabel('cumulative reward')
    ax.set_title(title)
    ax.grid(visible=True, which='both', alpha=0.5)
    ax.legend(title=legend_title, loc='upper left')

    plt.show()


def plot_regret():
    return


def _test_plot():

    # example on using plot function
    plt.rcParams['savefig.dpi'] = 300

    eps = [0.1, 0.2, 0.3, 0.4, 0.5]
    fn_list = ['epsilon_' + str(e) + '.csv' for e in eps]
    fn_list.append('annealing_epsilon_greedy.csv')
    legend_list = [str(e) for e in eps]
    legend_list.append('jdk')

    plot_cumulative_reward(fn_list, legend_list, fp='./logs/epsilon_greedy_test/', title='ss', legend_title='dd')


def _test_cal_baseline():

    from chem_arms import ChemArm
    import itertools

    # build chem arms
    dataset_url = 'https://raw.githubusercontent.com/beef-broccoli/ochem-data/main/deebo/aryl-conditions.csv'
    names = ('base_smiles', 'solvent_smiles')  # same names with column name in df
    base = ['O=C([O-])C.[K+]', 'O=C([O-])C(C)(C)C.[K+]']
    solvent = ['CC(N(C)C)=O', 'CCCC#N']
    vals = list(itertools.product(base, solvent))  # sequence has to match what's in "names"
    arms = list(map(lambda x: ChemArm(x, names, dataset_url), vals))

    # test basline
    calculate_baseline(arms)


if __name__ == '__main__':
    # example on using plot function
    plt.rcParams['savefig.dpi'] = 300

    fn_list = ['ucb1_test.csv', 'ucb1_tuned_test.csv']
    legend_list = ['ucb1', 'ucb1 tuned']

    plot_probs_choosing_best_arm(fn_list, legend_list, best_arm_index=4, fp='./logs/ucb1/', title='ucb1', legend_title='algos')