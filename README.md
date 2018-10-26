[中文][1]

[English][2]

## 介绍
关于**社区发现**和**Girvan_Newman算法**：

 - 社区发现：[Wiki][3]
 - 我的博客：[GN算法][4]，  [针对加权图的GN算法][5]
 - Girvan–Newman算法：[Wiki][6]
        

## 实现：

### Girvan_Newman算法

**Zachary's karate club网络：**
![Zachary's karate club][7]

**划分后的网络：**
![Zachary's karate club][8]

### 针对加权网络的Girvan_Newman算法

**Les Miserables网络：**
![Les miserables][9]

**划分后的网络：**
![Les miserables][10]

> 建议使用 [Gephi](https://gephi.org/ "Gephi") 显示数据集文件，可以为网络提供一个非常直观的展示

## 数据集 
**Zachary's karate club**: social network of friendships between 34 members of a karate club at a US university in the 1970s. W. W. Zachary, An information flow model for conflict and fission in small groups, Journal of Anthropological Research 33, 452-473 (1977).

**Les Miserables**: coappearance weighted network of characters in the novel Les Miserables. D. E. Knuth, The Stanford GraphBase: A Platform for Combinatorial Computing, Addison-Wesley, Reading, MA (1993).

这两个数据集均来自Gephi  的 [Sample Datasets](https://github.com/gephi/gephi/wiki/Datasets "Datasets")

Gephi sample datasets 提供了有非常丰富的关于网络的数据集

## 参考文献 

Newman M E J, Girvan M. Finding and evaluating community structure in networks[J]. Physical review E, 2004, 69(2): 026113.

------------

## Introduction
Some about **Community Structure**和**Girvan–Newman Algorithm**：

 - Community Structure：[Wiki][11]
 - My post(Chinese) ：[GN算法][12]，  [针对加权图的GN算法][13]
 - Girvan–Newman algorithm：[Wiki][14]

## Implementation：

### Girvan_Newman Algorithm

**Original Network：**
![Zachary's karate club][15]

**Divided network：**
![Zachary's karate club][16]

### Girvan_Newman Algorithm for weighted graph

**Original Network：**
![Lesmiserables][17]

**Divided network：**
![Lesmiserables][18]

> It is recommended to use [Gephi](https://gephi.org/ "Gephi") to display dataset files. And it can provide a very intuitive presentation of networks

## Datasets

### The Girvan_Newman algorithm uses the Zachary's karate club dataset
**Zachary's karate club**: social network of friendships between 34 members of a karate club at a US university in the 1970s. W. W. Zachary, An information flow model for conflict and fission in small groups, Journal of Anthropological Research 33, 452-473 (1977).

### The weighted Girvan_Newman algorithm uses the Les Miserables dataset
**Les Miserables**: coappearance weighted network of characters in the novel Les Miserables. D. E. Knuth, The Stanford GraphBase: A Platform for Combinatorial Computing, Addison-Wesley, Reading, MA (1993).

Both datasets are from [Gephi sample datasets](https://github.com/gephi/gephi/wiki/Datasets "Datasets")

## References
Newman M E J, Girvan M. Finding and evaluating community structure in networks[J]. Physical review E, 2004, 69(2): 026113.


  [1]: https://github.com/sikasjc/CommunityDetection#%E4%BB%8B%E7%BB%8D
  [2]: https://github.com/sikasjc/CommunityDetection#introduction
  [3]: https://en.wikipedia.org/wiki/Community_structure
  [4]: https://sikasjc.coding.me/2017/12/20/GN/
  [5]: https://sikasjc.github.io/2018/04/28/weighted_GN/
  [6]: https://en.wikipedia.org/wiki/Girvan%E2%80%93Newman_algorithm
  [7]: https://i.postimg.cc/X7GXdNws/79561109.png
  [8]: https://i.postimg.cc/x8q8snBT/17264809.png
  [9]: https://i.postimg.cc/fRv3T27s/75989614.png
  [10]: https://i.postimg.cc/m2CzK2tt/8315054.png
  [11]: https://en.wikipedia.org/wiki/Community_structure
  [12]: https://sikasjc.coding.me/2017/12/20/GN/
  [13]: https://sikasjc.github.io/2018/04/28/weighted_GN/
  [14]: https://en.wikipedia.org/wiki/Girvan%E2%80%93Newman_algorithm
  [15]: https://i.postimg.cc/X7GXdNws/79561109.png
  [16]: https://i.postimg.cc/x8q8snBT/17264809.png
  [17]: https://i.postimg.cc/fRv3T27s/75989614.png
  [18]: https://i.postimg.cc/m2CzK2tt/8315054.png
