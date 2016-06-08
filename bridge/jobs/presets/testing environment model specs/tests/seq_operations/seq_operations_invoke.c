#include <linux/module.h>
#include <linux/seq_file.h>
#include <linux/emg/test_model.h>
#include <verifier/nondet.h>

struct file *file;
struct inode *inode;

static void *ldv_start_callback(struct seq_file *file, loff_t *pos)
{
	ldv_invoke_reached();
	return 0;
}

static void ldv_stop_callback(struct seq_file *file, void *iter_ptr)
{
	ldv_invoke_reached();
}

static const struct seq_operations ldv_ops = {
	.start = ldv_start_callback,
	.stop  = ldv_stop_callback,
};

static int __init ldv_init(void)
{
	return seq_open(file, &ldv_ops);
}

static void __exit ldv_exit(void)
{
	seq_release(inode,file);
}

module_init(ldv_init);
module_exit(ldv_exit);
