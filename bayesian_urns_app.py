import matplotlib.pyplot as plt
import streamlit as st

def binomial(n,k):
    if not 0<= k<= n:
        return 0
    a=1
    for t in range(min(k, n-k)):
        a*=n
        a//=t+1
        n-=1
    return a

class Urns:
    '''Urn has M balls of two colours. N balls are drawn with/without replacement.
        parameters
        ==========
        M int 
            total number of balls in the urn
        N int
            number of draws in every experiment
        K_b list of integers
            number of occurence of ball of interest in each experiment
        replacement boolean
            if true, the sampling are done with replacement
            if false, the sampling is done without replacement
        p float
            significance level set to 0.1 as default
        '''
    def __init__(self, M, N, K_b, replacement, p):
        self.M=M
        self.N=N
        self.K_b = K_b
        self.replacement = replacement
        self.p = p
        if replacement:
            self.range_b = list(range(1,M))
        else:
            self.range_b = list(range(max(K_b), M+min(K_b)-N)) 
            
        l = len(self.range_b)
        # initial prior uniform
        self.posteriors=[[1/l]*l]
        
    def prior(self):
        '''Return prior probability.'''
        return self.posteriors[-1]
    
    def random_process(self, b, k_b):
        '''Return probability distribution of random process.
            Binomial if sampling with replacement.
            Hypergeometric if sampling without replacement.'''
        if self.replacement:
            q = b/self.M
            return binomial(self.N, k_b) * (q**(k_b)) * (1-q)**(self.N -k_b)
        else:
            return (binomial(b, k_b) * binomial(self.M-b, self.N-k_b)) / binomial(self.M, self.N)
        
    def normalization(self, k_b):
        '''Return normalization factor for probability updating.'''
        norm = 0
        for i, b in enumerate(self.range_b):
            norm+= self.random_process(b, k_b) * self.prior()[i]
        return norm
    
    def posterior(self,k_b):
        '''Return the posterior probability.'''
        random_process = [self.random_process(b, k_b) for b in self.range_b]
        return [a*b/self.normalization(k_b) for a,b in zip(random_process , self.prior())]
    
    def update_posteriors(self):
        '''Return all posterior probabilities that are updated due to experiments.'''
        for i in range(len(self.K_b)):
            self.posteriors.append(list(self.posterior(self.K_b[i])))
        return self.posteriors   
    
    def plot_posterior(self):
        '''Plot the final posterior probability, its maximum, and the most probable value.'''
        # check if probabilities has been updated
        st.subheader('Probability')
        if len(self.posteriors)==1:
            self.update_posteriors()
        posterior = self.posteriors[-1]
        m = max(posterior)
        i = posterior.index(m)
        fig, ax = plt.subplots(figsize = (12,7))
        ax.plot(self.range_b, posterior)
        ax.vlines(self.range_b[i], 0, m, colors='red')
        ax.hlines(m, 0, self.range_b[i], colors='blue')
        st.pyplot(fig)
        st.write("The maximum probability is {:.04f}.".format(m))
        st.write("The most likely number of black balls is {} out of {}.".format(self.range_b[i], self.M))
        if (1-m)<= self.p:
            st.write("The hypothesis that the number of black balls equals {} is accepted (significance level {}).".format(self.range_b[i], p))
        else:
            st.write("The hypothesis that the number of black balls equals {} is rejected (significance level {}).".format(self.range_b[i], p))

# Streamlit App        

st.title('Bayesian Urns')
st.sidebar.write("This is a simple application that does inference when sampling from an urn with two distict types of balls (say black and white for the sake of concreteness). Sampling can be done with or without replacement.")

# input the total number of balls in the urn
M = st.sidebar.number_input('Enter the total number of balls in the urn: ', 2)


# input the number of samples
N = st.sidebar.number_input('Enter the number of balls per experiment: ', 1)

# input replacement
replacement = st.sidebar.selectbox('Specify whether sampling is with or without replacement:', ['With replacement', 'Without replacement'])
if replacement == 'With replacement':
    replacement = True
else:
    replacement = False
    
# input number of positive cases per experiment
K_b = st.sidebar.text_input('Enter the number of black balls per experiment separated by space:', 1)

K_b = [int(k_b) for k_b in K_b.split()]

# enter significance level for hypothesis testing
p = st.sidebar.number_input('Enter significance level:', 0.1)

# offer option to see the input
expand_input = st.beta_expander("Input")
expand_input.write(f"Number of balls in the urn {M} ; Number of balls per experiment {N} ; Number of black balls per experiment {K_b}; Significance level {p}")

# instance of the urn
u = Urns(int(M),int(N), K_b, replacement, p)

# update posteriors
u.update_posteriors()                                                                                              
posterior = u.posteriors[-1]
m = max(posterior)
i = posterior.index(m)

# Create plot
u.plot_posterior()
