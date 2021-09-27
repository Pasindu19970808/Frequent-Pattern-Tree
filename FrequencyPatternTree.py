#This script successfully builds the FP Tree
from collections import Counter, defaultdict
import copy
import csv

#The input is a dictionary where the key is transaction ID (1,2,3,4....)
#The value is the transaction


i = 1
transaction_dict = {}
with open(r'.\Groceries.csv', newline = '\n') as datafile:
    datareader = csv.reader(datafile)
    for row in datareader:
        transaction_dict[i] = [j.strip() for j in row if j != '']
        i += 1 

#Nodes are created to make linked lists containing childrens information and parents information
class Node:
    def __init__(self,name,frequency,parent_name = None,parent_obj = None):
        self.name = name
        self.count = frequency
        self.parent_name = parent_name
        self.parent = parent_obj
        self.children = {}
        #self.pointer is used to point to the same item in another transaction
        #This makes it easier to traverse the FP tree without having to start from the root everytime
        self.pointer = None
    def increment(self):
        self.count += 1

#This function takes the result of function "get_item_frequency" and removes all items below the support value from the transaction dictionary
def remove_items_below_sup(transaction_dict,support):
    count = Counter()
    for transaction in transaction_dict:
        count.update(transaction_dict[transaction])
    final_counts = {i[0]:i[1] for i in sorted(count.items(), key = lambda x: x[1],reverse=True) if i[1] >= support}
    #this allows to ensure a consistent order of sorted items, even if 2 or more items have the same support
    final_counts_idx_order = dict(zip(final_counts.keys(),range(len(final_counts.keys()))))
    for transaction in transaction_dict:
        transaction_dict[transaction] = sorted([i for i in transaction_dict[transaction] if (i in final_counts.keys())],key = lambda x: final_counts_idx_order[x])
    return transaction_dict,final_counts


#traverse one transaction
def traverse_one_transaction(transaction,root_node,currentidx,pointerTable):
    if currentidx < len(transaction):
        item = transaction[currentidx]
        if item in root_node.children:
            #If we are revisiting a node we only want it to increment
            root_node.children[item].increment()
        else:
            child_node = Node(item,1,parent_name = root_node.name,parent_obj=root_node)
            root_node.children[item] = child_node
            #Updating the pointer table
            #We only want the pointer table to be updated if we are newly visiting a node
            if pointerTable[item][1] == None:
                #If there is no node in the given item of the pointerTable
                #This means that this is the first time we are visiting this item
                #Hence we create a new node here by adding the root_node.children[item]
                pointerTable[item][1] = root_node.children[item]
            else:
                
                current_item_node= pointerTable[item][1]
                while current_item_node.pointer != None:
                    current_item_node = current_item_node.pointer
                current_item_node.pointer = root_node.children[item]
        traverse_one_transaction(transaction,root_node.children[item],currentidx + 1,pointerTable)



def create_fp_tree(transaction_dict):
    pointerTable = defaultdict(int)

    #Counting frequency of each item 
    for transaction in transaction_dict:
        for item in transaction_dict[transaction]:
            #In the context of a conditional tree for a particular item, this step allows us to get the count
            #of prefix attached to the concerned suffix item, making counting of an itemset much faster 
            pointerTable[item] += 1

    #we want the pointerTable to point to the places where the particular item is being kept in the FP tree
    for item in pointerTable:
        pointerTable[item] = [pointerTable[item],None]

    #Starting null node    
    root_node = Node('Null',1,None)
    for trans in transaction_dict:
        traverse_one_transaction(transaction = transaction_dict[trans],root_node = root_node,currentidx = 0, pointerTable = pointerTable)
    return root_node,pointerTable



#Gets the conditional pattern base of each item
def find_paths(item,pointerTable):
    #build a default dictionary to add in all the paths with the item suffix in concern
    paths_list = list()
    item_suffix_node = pointerTable[item][1]
    collect_path(item_suffix_node,paths_list)
    while item_suffix_node.pointer != None:
        item_suffix_node = item_suffix_node.pointer
        collect_path(item_suffix_node,paths_list)
    if len(paths_list) >= 1:    
        return {i:path for i,path in zip(range(len(paths_list)),paths_list)},pointerTable[item][0]
    else:
        return None,pointerTable[item][0]
        

def collect_path(item_suffix_node,paths_list):
    #some transactions are identical, or some transactions follow the same path from root to a certain item 
    #we need to collect all such paths 
    suffix_count = item_suffix_node.count
    path = list()
    while item_suffix_node.name != "Null":
        path.append(item_suffix_node.name)
        item_suffix_node = item_suffix_node.parent
    if len(path[::-1][:-1]) >= 1:
        for i in range(0,suffix_count):
            paths_list.append(path[::-1][:-1])


def mine_tree(item,pointerTable,freq_itemset,freq_itemsetlist,minsup):
    #return all the paths with the suffix under concern
    suffix_paths,suffix_count = find_paths(item,pointerTable)
    #return the sorted transaction for the item under concern
    if suffix_paths != None:
        sorted_dict,final_counts = remove_items_below_sup(suffix_paths,minsup)
        items = list(final_counts.keys())[::-1]
        #Now we build the new tree based on the conditional bases from sorted_dict
        #This also produces the newpointerTable
        conditional_base_tree,newpointerTable = create_fp_tree(sorted_dict)
        for item in items:
            if newpointerTable[item][1] != None:
                new_itemset = freq_itemset.copy()
                new_itemset.add(item)
                if newpointerTable[item][0] >= minsup:
                    freq_itemsetlist.append((new_itemset,newpointerTable[item][0]))
                mine_tree(item,newpointerTable,new_itemset,freq_itemsetlist,minsup)





#items: all the sorted items that have made greater support than minimum sup
#pointerTable : this allows us to find the paths for each suffix
def find_frequent_itemsets(items,pointerTable,minsup):
    freq_itemsetlist = list()
    for item in items[::-1]:
        freq_itemset = set()
        freq_itemset.add(item)
        initial_suffix_paths, initial_suffix_count = find_paths(item,pointerTable)
        freq_itemsetlist.append((freq_itemset,initial_suffix_count))
        mine_tree(item,pointerTable,freq_itemset,freq_itemsetlist,minsup)
    return freq_itemsetlist



transaction_dict,final_count = remove_items_below_sup(transaction_dict,2)

fp_tree, pointerTable = create_fp_tree(transaction_dict)

find_frequent_itemsets(list(final_count.keys()),pointerTable,2)

print(find_frequent_itemsets(list(final_count.keys()),pointerTable,2))

print(final_count)






