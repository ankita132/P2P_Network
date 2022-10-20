import matplotlib.pyplot as plt

def find_lines(file_name):
    timeVal = 0.0
    count = 0
    with open(file_name) as f:
        for line in f:
            if("Average runtime" in line):
                s = line.split()
                timeVal += float(s[len(s)-2])
                count += 1
    
    return timeVal/count

if __name__ == '__main__':
    ax = plt.subplot()
    
    ax.axhline(0, color='grey', linewidth=0.8)
    ax.set_title('Runtime vs Buyers sending requests to 1 Seller')
    ax.set_ylabel('Time taken in milliseconds')
    times = []
    times.append(find_lines('output_1.txt'))
    times.append(find_lines('output_2.txt'))
    times.append(find_lines('output_3.txt'))
    times.append(find_lines('output_5.txt'))
    times.append(find_lines('output_4.txt'))

    neighbors = ['1 Buyer', '2 Buyers', '3 Buyers', '4 Buyers', '5 Buyers']
    #print(times)
    ax.set_xticks([0,1,2,3,4])
    ax.set_yticks(times)
    plt.bar(neighbors,times)
    plt.savefig('./images/NeighborsVsRuntime.png')