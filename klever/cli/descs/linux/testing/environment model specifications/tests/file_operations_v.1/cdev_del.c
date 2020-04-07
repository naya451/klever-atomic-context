/*
 * Copyright (c) 2018 ISP RAS (http://www.ispras.ru)
 * Ivannikov Institute for System Programming of the Russian Academy of Sciences
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <ldv/linux/emg/test_model.h>
#include <ldv/verifier/nondet.h>

static int ldv_open(struct inode *inode, struct file *filp)
{
	ldv_invoke_callback();
	return 0;
}

static int ldv_release(struct inode *inode, struct file *filp)
{
	ldv_invoke_callback();
	return 0;
}

static struct file_operations ldv_fops = {
	.open		= ldv_open,
	.release	= ldv_release,
	.owner		= THIS_MODULE,
};

static struct cdev ldv_cdev = {
	.ops = & ldv_fops,
};

static int __init ldv_init(void)
{
	int flip_a_coin;

	flip_a_coin = ldv_undef_int();
	if (flip_a_coin) {
		ldv_register();
		cdev_init(&ldv_cdev, &ldv_fops);
		cdev_del(&ldv_cdev);
		ldv_deregister();
	}
	return 0;
}

static void __exit ldv_exit(void)
{
	/* pass */
}

module_init(ldv_init);
module_exit(ldv_exit);
