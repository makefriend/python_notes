import tensorflow as tf

random_float = tf.random.uniform(shape=())

zero_vector = tf.zeros(shape=2)

print(random_float, zero_vector)

# 定义两个2×2的常量矩阵
A = tf.constant([[1., 2.], [3., 4.]])
B = tf.constant([[5., 6.], [7., 8.]])

# 查看矩阵A的形状、类型和值
print(A.shape)  # 输出(2, 2)，即矩阵的长和宽均为2
print(A.dtype)  # 输出<dtype: 'float32'>
print(A.numpy())  # 输出[[1. 2.]
#      [3. 4.]]


C = tf.add(A, B)
print(C)
